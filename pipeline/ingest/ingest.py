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
import lasairLogging

stop = False
log = None
sigterm_raised = False

def sigterm_handler(signum, frame):
    global sigterm_raised
    sigterm_raised = True
    print("Caught SIGTERM")

signal.signal(signal.SIGTERM, sigterm_handler)

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

def msg_text(message):
    """msg_text. Remove postage stamp cutouts from an alert message.

    Args:
        message:
    """
    message_text = {k: message[k] for k in message
                    if k not in ['cutoutDifference', 'cutoutTemplate', 'cutoutScience']}
    return message_text

def store_images(message, store, diaSourceId):
    global log
    try:
        for cutoutType in ['cutoutDifference', 'cutoutTemplate']:
            content = message[cutoutType]
            filename = '%d_%s' % (diaSourceId, cutoutType)
            store.putObject(filename, content)
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

    # if it does not have all the LSST attributes, don't try to ingest
    if not 'diaSourceId' in alert['diaSource'] or not alert['diaSource']['diaSourceId']:
        return 0

    diaSourceList            = []
    diaForcedSourceList      = []
    diaNondetectionLimitList = []
    ssObjectList             = []
    # Make a list of diaSource, diaForcedSource, diaNondetection in time order
    if 'diaSource' in alert and alert['diaSource'] != None:
        if 'prvDiaSources' in alert and alert['prvDiaSources'] != None:
            diaSourceList = alert['prvDiaSources'] + [alert['diaSource']]
        else:
            diaSourceList = [alert['diaSource']]

        if 'prvDiaForcedSources' in alert and alert['prvDiaForcedSources'] != None:
            diaForcedSourceList = alert['prvDiaForcedSources']

        if 'prvDiaNondetectionLimits' in alert and alert['prvDiaNondetectionLimits'] != None:
            diaNondetectionLimitList = alert['prvDiaNondetectionLimits']

        if 'ssObject' in alert and alert['ssObject'] != None:
            ssObjectList = [alert['ssObject']]

    if len(diaSourceList) == 0:
        # No point continuing. We have no data.
        print('No diaSources')
        return 0

    # Add the htm16 IDs in bulk. Could have done it above as we iterate through the diaSource,
    # but the new C++ bulk code is 100 times faster than doing it one at a time.
    # Note that although we are inserting them into cassandra, we are NOT using
    # HTM indexing inside Cassandra. Hence this is a redundant column.

    # Now add the htmid16 value into each dict.
    htm16s = htmCircle.htmIDBulk(16, [[x['ra'],x['decl']] for x in diaSourceList])
    for i in range(len(diaSourceList)):
        diaSourceList[i]['htm16'] = htm16s[i]
    executeLoad(cassandra_session, 'diaSources', diaSourceList)

    if len(diaForcedSourceList) > 0:
        executeLoad(cassandra_session, 'diaForcedSources', diaForcedSourceList)

    if len(diaNondetectionLimitList) > 0:
        executeLoad(cassandra_session, 'diaNondetectionLimits', diaNondetectionLimitList)

    if len(ssObjectList) > 0:
        # should there be HTM for these?
        executeLoad(cassandra_session, 'ssObjects', ssObjectList)

    return len(diaSourceList)

def handle_alert(alert, image_store, producer, topic_out, cassandra_session):
    """handle_alert.
    Filter to apply to each alert.

    Args:
        alert:
        image_store:
        producer:
        topic_out:
    """
    global log
    # here is the part of the alert that has no binary images
    alert_noimages = msg_text(alert)
    if not alert_noimages:
        log.error('ERROR:  in ingest/ingest: No json in alert')
        return None  # ingest batch failed

    diaSourceId = alert_noimages['diaSource']['diaSourceId']

    # store the fits images
    if image_store:
        if store_images(alert, image_store, diaSourceId) == None:
            log.error('ERROR: in ingest/ingest: Failed to put cutouts in file system')
            return None   # ingest batch failed

    # Call on Cassandra
    try:
        ndiaSource = insert_cassandra(alert_noimages, cassandra_session)
    except:
        log.error('ERROR in ingest/ingest: Cassandra insert failed')
        return None  # ingest batch failed

    # produce to kafka
    if producer is not None:
        try:
            s = json.dumps(alert_noimages)
            producer.produce(topic_out, json.dumps(alert_noimages))
        except Exception as e:
            log.error("ERROR in ingest/ingest: Kafka production failed for %s" % topic_out)
            log.error("ERROR:", e)
            sys.stdout.flush()
            return None   # ingest failed

    return 1

def run_ingest(args):
    """run.
    """
    global stop
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

    # set up image store in shared file system
    if fitsdir and len(fitsdir) > 0:
        image_store  = objectStore.objectStore(suffix='fits', fileroot=fitsdir)
    else:
        log.error('ERROR in ingest/ingestBatch: No image directory found for file storage')
        sys.stdout.flush()
        image_store = None

    # connect to cassandra cluster
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
        'default.topic.config': {'auto.offset.reset': 'smallest'},

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
    ntotalalert = 0   # number since this program started
    log.info('INGEST starts %s' % now())

    # put status on Lasair web page
    ms = manage_status.manage_status(settings.SYSTEM_STATUS)

    while ntotalalert < maxalert:

        msg = consumer.poll(timeout=5)

        # no messages available
        if msg is None:
            end_batch(consumer, producer, ms, nalert, ndiaSource)
            nalert = ndiaSource = 0
            log.debug('no more messages ... sleeping %d seconds' % settings.WAIT_TIME)
            sys.stdout.flush()
            time.sleep(settings.WAIT_TIME)
            continue

        # read the avro contents
#        try:
        bytes_io = io.BytesIO(msg.value())
        alert = fastavro.schemaless_reader(bytes_io, pschema)
#        except:
#            log.error('ERROR in ingest/ingest: ', msg.value())
#            break

        if stop:
            # clean shutdown - this should stop the consumer and commit offsets
            log.info("Stopping ingest")
            sys.stdout.flush()
            break

        # Apply filter to each alert
        idiaSource = handle_alert(alert, image_store, producer, topic_out, cassandra_session)

        if idiaSource == None:
            log.info('Ingestion failed ')
            return 0

        nalert += 1
        ntotalalert += 1
        ndiaSource += idiaSource

        # every so often commit, flush, and update status
        if nalert >= 250:
            end_batch(consumer, producer, ms, nalert, ndiaSource)
            nalert = ndiaSource = 0
            # check for lockfile
            if not os.path.isfile(settings.LOCKFILE):
                log.info('Lockfile not present')
                stop = True

    # if we exit this loop, clean up
    log.info('Shutting down')
    end_batch(consumer, producer, ms, nalert, ndiaSource)

    # shut down kafka consumer
    consumer.close()

    # shut down the cassandra cluster
    if cassandra_session:
        cluster.shutdown()

    # did we get any alerts
    if ntotalalert > 0: return 1
    else:               return 0

def end_batch(consumer, producer, ms, nalert, ndiaSource):
    global log
    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    log.info('%s %d alerts %d diaSource' % (date, nalert, ndiaSource))
    # if this is not flushed, it will run out of memory
    if producer is not None:
        producer.flush()

    # commit the alerts we have read
    consumer.commit()
    sys.stdout.flush()

    # update the status page
    nid  = date_nid.nid_now()
    ms.add({'today_alert':nalert, 'today_diaSource':ndiaSource}, nid)

if __name__ == "__main__":
    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("ingest")

    signal.signal(signal.SIGTERM, sigterm_handler)

    args = docopt(__doc__)
    rc = run_ingest(args)
    # rc=1, got alerts, more to come
    # rc=0, got no alerts
    sys.exit(rc)
