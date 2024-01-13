"""
Ingestion code for Lasair. Takes a stream of AVRO, splits it into
FITS cutouts to Ceph, Lightcurves to Cassandra, and JSON versions of 
the AVRO packets, but without the cutouts, to Kafka.
Kafka commit os every 1000 alerts, and before exit.
Usage:
    ingest.py [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN | --nid=NID] 
              [--topic_out=TOUT]

Options:
    --nprocess=NP      Number of processes to use [default:1]
    --maxalert=MAX     Number of alerts to process, default is from settings.
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, or
    --nid=NID          ZTF night number to use (default today)
    --topic_out=TOUT   Kafka topic for output [default:ztf_sherlock]
"""

import sys
from docopt import docopt
from datetime import datetime
from confluent_kafka import Consumer, Producer, KafkaError
from gkhtm import _gkhtm as htmCircle
from cassandra.cluster import Cluster
from gkdbutils.ingesters.cassandra import executeLoad
import os, time, json, io, fastavro, signal

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import objectStore, manage_status, date_nid, slack_webhook
import cutoutStore
import lasairLogging

stop = False
log = None
sigterm_raised = False

def sigterm_handler(signum, frame):
    global sigterm_raised
    sigterm_raised = True
    #print("Caught SIGTERM")

signal.signal(signal.SIGTERM, sigterm_handler)

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

def store_images(message, store, diaSourceId, imjd, diaObjectId):
    global log
    try:
        for cutoutType in ['cutoutDifference', 'cutoutTemplate']:
            if not cutoutType in message: 
                continue
            content = message[cutoutType]
            cutoutId = '%d_%s' % (diaSourceId, cutoutType)
            # store may be cutouts or cephfs
            if settings.USE_CUTOUTCASS:
                store.putCutout(cutoutId, imjd, diaObjectId, content)
            else:
                store.putObject(cutoutId, imjd, content)
        return True
    except Exception as e:
        log.error('ERROR in ingest/ingest: ', e)
        return None # failure of batch

def insert_cassandra(alert, cassandra_session):
    """insert_casssandra.
    Creates an insert for cassandra
    a query for inserting it.

    Args:
        alert:
    """
    global log

    # if this is not set, then we are not doing cassandra
    if not cassandra_session:
        return None   # failure of batch

    executeLoad(cassandra_session, 'DiaObjects', [alert['diaObject']])
    # Note that although we are inserting them into cassandra, we are NOT using
    # HTM indexing inside Cassandra. Hence this is a redundant column.

    # Now add the htmid16 value into each dict.

    diaSourcesList = alert['diaSourcesList']
#    htm16s = htmCircle.htmIDBulk(16, [[x['ra'],x['decl']] for x in diaSourcesList])
#    for i in range(len(diaSourcesList)):
#        diaSourcesList[i]['htm16'] = htm16s[i]
    if len(diaSourcesList) > 0:
        executeLoad(cassandra_session, 'DiaSources', diaSourcesList)

    if len(alert['forcedSourceOnDiaObjectsList']) > 0:
        executeLoad(cassandra_session, 'ForcedSourceOnDiaObjects', alert['forcedSourceOnDiaObjectsList'])

    return len(diaSourcesList)

def handle_alert(lsst_alert, image_store, producer, topic_out, cassandra_session, timers):
    """handle_alert.
    Filter to apply to each alert.

    Args:
        lsst_alert:
        image_store:
        producer:
        topic_out:
    """
    global log

    # Build a new alert packet
    diaObject                 = lsst_alert['DiaObject']
    forcedSourceOnDiaObjectsList      = lsst_alert['ForcedSourceOnDiaObjectList']
    diaSourcesList            = lsst_alert['DiaSourceList']
    diaSourcesList = sorted(diaSourcesList, key=lambda x: x['midPointTai'], reverse=True)

    if len(diaSourcesList) > 0:
        lastSource = diaSourcesList[0]

        # ID for the latest detection, this is what the cutouts belong to
        diaSourceId = lastSource['diaSourceId']

        # MJD for storing images
        imjd = int(lastSource['midPointTai'])

    # objectID
    diaObjectId = diaObject['diaObjectId']

    # store the fits images
    timers['icutout'].on()
    if image_store:
        if store_images(lsst_alert, image_store, diaSourceId, imjd, diaObjectId) == None:
            log.error('ERROR: in ingest/ingest: Failed to put cutouts in file system')
    timers['icutout'].off()

    alert = {
        'diaObject':                 diaObject,
        'diaSourcesList':            diaSourcesList,
        'forcedSourceOnDiaObjectsList':      forcedSourceOnDiaObjectsList,
    }

    # Add the htm16 IDs in bulk. Could have done it above as we iterate through the diaSource,
    # but the new C++ bulk code is 100 times faster than doing it one at a time.

    # Call on Cassandra
    try:
        timers['icassandra'].on()
        ndiaSource = insert_cassandra(alert, cassandra_session)
        timers['icassandra'].off()
    except Exception as e:
        log.error('ERROR in ingest/ingest: Cassandra insert failed' + str(e))
        return 0  # ingest batch failed

    # produce to kafka
    timers['ikafka'].on()
    if producer is not None:
        try:
            s = json.dumps(alert)
            producer.produce(topic_out, json.dumps(alert))
        except Exception as e:
            log.error("ERROR in ingest/ingest: Kafka production failed for %s" % topic_out)
            log.error("ERROR:", e)
            sys.stdout.flush()
            return None   # ingest failed
    timers['ikafka'].off()

    return (len(diaSourcesList), len(forcedSourceOnDiaObjectsList))

def run_ingest(args, timers):
    """run.
    """
    global sigterm_raised
    global log

    # if logging wasn't set up in __main__ then do it here
    if not log:
        log = lasairLogging.getLogger("ingest")

    signal.signal(signal.SIGTERM, sigterm_handler)

    if args['--topic_in']:
        topic_in = args['--topic_in']
    elif args['--nid']:
        nid = int(args['--nid'])
        date = date_nid.nid_to_date(nid)
        topic_in  = 'ztf_' + date + '_programid1'
    else:
        # get all alerts from every nid
        topic_in = '^ztf_.*_programid1$'

    if args['--topic_out']:
        topic_out = args['--topic_out']
    else:
        topic_out = 'ztf_ingest'
    
    if args['--group_id']:
        group_id = args['--group_id']
    else:
        group_id = settings.KAFKA_GROUPID
    
    if args['--maxalert']:
        maxalert = int(args['--maxalert'])
    else:
        maxalert = sys.maxsize  # largest possible integer
    
    try:
        fitsdir = settings.IMAGEFITS
    except:
        fitsdir = None

    # check for lockfile
    if not os.path.isfile(settings.LOCKFILE):
        log.info('Lockfile not present')
        return  0

    # set up image store in Cassandra or shared file system
    if settings.USE_CUTOUTCASS:
        image_store = cutoutStore.cutoutStore()
        if image_store.session == None:
            image_store = None
    elif fitsdir and len(fitsdir) > 0:
        image_store  = objectStore.objectStore(suffix='fits', fileroot=fitsdir)
    else:
        log.error('ERROR in ingest/ingestBatch: Cannot store cutouts. USE_CUTOUTCASS=%s' % settings.USE_CUTOUTCASS)
        sys.stdout.flush()
        image_store = None

    # connect to cassandra cluster for alerts (not cutouts)
    try:
        cluster = Cluster(settings.CASSANDRA_HEAD)
        cassandra_session = cluster.connect()
        cassandra_session.set_keyspace('lasair')
    except Exception as e:
        log.error("ERROR in ingest/ingestBatch: Cannot connect to Cassandra", e)
        sys.stdout.flush()
        cassandra_session = None

    f = open(settings.SCHEMA)
    schema = json.loads(f.read())
    pschema = fastavro.parse_schema(schema)

    # set up kafka consumer
    log.info('Consuming from %s' % settings.KAFKA_SERVER)
    log.info('Topic_in       %s' % topic_in)
    log.info('Topic_out      %s' % topic_out)
    log.info('group_id       %s' % group_id)
    log.info('maxalert       %d' % maxalert)

    consumer_conf = {
        'bootstrap.servers'   : '%s' % settings.KAFKA_SERVER,
        'group.id'            : group_id,
        'enable.auto.commit'  : False,
        'default.topic.config': {'auto.offset.reset': 'earliest'},

        # wait twice wait time before forgetting me
        'max.poll.interval.ms': 50*settings.WAIT_TIME*1000,  
    }

    try:
        consumer = Consumer(consumer_conf)
    except Exception as e:
        log.error('ERROR in ingest/ingestBatch: Cannot connect to Kafka', e)
        sys.stdout.flush()
        return 1
    consumer.subscribe([topic_in])

    # set up kafka producer
    producer_conf = {
        'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
        'client.id': 'client-1',
    }
    producer = Producer(producer_conf)
    log.info('Producing to   %s' % settings.KAFKA_SERVER)

    nalert = 0        # number not yet send to manage_status
    ndiaSource = 0    # number not yet send to manage_status
    nforcedSource = 0    # number not yet send to manage_status
    ntotalalert = 0   # number since this program started
    log.info('INGEST starts %s' % now())

    # put status on Lasair web page
    ms = manage_status.manage_status(settings.SYSTEM_STATUS)
    timers = {}
    for name in ['icutout', 'icassandra', 'ikafka', 'itotal']:
        timers[name] = manage_status.timer(name)

    timers['itotal'].on()
    while ntotalalert < maxalert:
        if sigterm_raised:
            # clean shutdown - this should stop the consumer and commit offsets
            log.info("Stopping ingest")
            sys.stdout.flush()
            break

        msg = consumer.poll(timeout=5)

        # no messages available
        if msg is None:
            end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource, timers)
            nalert = ndiaSource = 0
            log.debug('no more messages ... sleeping %d seconds' % settings.WAIT_TIME)
            sys.stdout.flush()
            time.sleep(settings.WAIT_TIME)
            continue

        # read the avro contents
#        try:
        bytes_io = io.BytesIO(msg.value())
        lsst_alert = fastavro.schemaless_reader(bytes_io, pschema)
#        except:
#            log.error('ERROR in ingest/ingest: ', msg.value())
#            break

        # Apply filter to each alert
        (idiaSource,iforcedSource) = \
                handle_alert(lsst_alert, image_store, producer, topic_out, cassandra_session, timers)

        nalert += 1
        ntotalalert += 1
        ndiaSource += idiaSource
        nforcedSource += iforcedSource

        # every so often commit, flush, and update status
        if nalert >= 250:
            end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource, timers)
            nalert = ndiaSource = nforcedSource = 0
            # check for lockfile
            if not os.path.isfile(settings.LOCKFILE):
                log.info('Lockfile not present')
                stop = True
    timers['itotal'].off()

    # if we exit this loop, clean up
    log.info('Shutting down')
    end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource, timers)

    # shut down kafka consumer
    consumer.close()

    # shut down the cassandra cluster
    if cassandra_session:
        cluster.shutdown()

    # did we get any alerts
    if ntotalalert > 0: return 1
    else:               return 0

def end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource, timers):
    global log
    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    log.info('%s %d alerts %d diaSource %d forcedSource' % (date, nalert, ndiaSource, nforcedSource))
    # if this is not flushed, it will run out of memory
    if producer is not None:
        producer.flush()

    # commit the alerts we have read
    consumer.commit()
    sys.stdout.flush()

    # update the status page
    nid  = date_nid.nid_now()
    ms.add({'today_alert':nalert, 'today_diaSource':ndiaSource}, nid)
    for name,td in timers.items():
        td.add2ms(ms, nid)

if __name__ == "__main__":
    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("ingest")

    signal.signal(signal.SIGTERM, sigterm_handler)

    nid  = date_nid.nid_now()
    args = docopt(__doc__)
    rc = run_ingest(args)
    # rc=1, got alerts, more to come
    # rc=0, got no alerts
    sys.exit(rc)

