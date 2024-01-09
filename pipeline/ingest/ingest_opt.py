# temporary version to test optimisations - will go away when merged

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
from gkdbutils.ingesters.cassandra import executeLoadAsync
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

signal.signal(signal.SIGTERM, sigterm_handler)

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

def store_images(message, store, diaSourceId, imjd, diaObjectId):
    """Store cutout images in the image store and return an array of
    futures to wait for (which may be empty if not using cassandra)."""
    global log
    try:
        futures = []
        for cutoutType in ['cutoutDifference', 'cutoutTemplate']:
            if not cutoutType in message: 
                continue
            content = message[cutoutType]
            cutoutId = '%d_%s' % (diaSourceId, cutoutType)
            # store may be cutouts or cephfs
            if settings.USE_CUTOUTCASS:
                result = store.putCutoutAsync(cutoutId, imjd, diaObjectId, content)
                futures.append(result)
            else:
                store.putObject(cutoutId, imjd, content)
        return futures
    except Exception as e:
        log.error('ERROR in ingest/ingest: ', e)
        return None # failure of batch

def insert_cassandra(alert, cassandra_session):
    result = insert_cassandra_multi([alert], cassandra_session)
    if result:
        return result

def insert_cassandra_multi(alerts, cassandra_session):
    """insert_casssandra.
    Creates an insert for cassandra
    a query for inserting it.

    Uses async load and returns a list of future objects.

    Args:
        alerts:
    """
    global log

    # if this is not set, then we are not doing cassandra
    if not cassandra_session:
        return None   # failure of batch

    futures = []

    data = []
    for alert in alerts:
        data.append(alert['diaObject'])

    futures += executeLoadAsync(cassandra_session, 'DiaObjects', data)
    # Note that although we are inserting them into cassandra, we are NOT using
    # HTM indexing inside Cassandra. Hence this is a redundant column.

    # Now add the htmid16 value into each dict.

    diaSourcesList = []
    for alert in alerts:
        diaSourcesList += alert['diaSourcesList']
#    htm16s = htmCircle.htmIDBulk(16, [[x['ra'],x['decl']] for x in diaSourcesList])
#    for i in range(len(diaSourcesList)):
#        diaSourcesList[i]['htm16'] = htm16s[i]
    if len(diaSourcesList) > 0:
        futures += executeLoadAsync(cassandra_session, 'DiaSources', diaSourcesList)

    forcedSourceOnDiaObjectsList = []
    for alert in alerts:
        forcedSourceOnDiaObjectsList += alert['forcedSourceOnDiaObjectsList']
    if len(forcedSourceOnDiaObjectsList) > 0:
        futures += executeLoadAsync(cassandra_session, 'ForcedSourceOnDiaObjects', forcedSourceOnDiaObjectsList)

    return futures

def handle_alert(lsst_alert, image_store, producer, topic_out, cassandra_session):
    """Handle a single alert"""
    results = handle_alerts([lsst_alert], image_store, producer, topic_out, cassandra_session)
    if results and len(results) > 0:
        return results[0]

def handle_alerts(lsst_alerts, image_store, producer, topic_out, cassandra_session):
    """Handle multiple alerts.
    Filter to apply to each alert.

    Args:
        lsst_alert:
        image_store:
        producer:
        topic_out:
    """
    global log

    image_futures = []
    cass_futures = []
    results = []

    # deal with images first
    for lsst_alert in lsst_alerts:

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
        if image_store:
            image_result = store_images(lsst_alert, image_store, diaSourceId, imjd, diaObjectId)
            if image_result == None:
                log.error('ERROR: in ingest/ingest: Failed to put cutouts in file system')
            else:
                image_futures += image_result

        results.append((len(diaSourcesList), len(forcedSourceOnDiaObjectsList)))

    # build the alerts
    alerts = []
    for lsst_alert in lsst_alerts:
        alert = {
            'diaObject':                 diaObject,
            'diaSourcesList':            diaSourcesList,
            'forcedSourceOnDiaObjectsList':      forcedSourceOnDiaObjectsList,
        }
        alerts.append(alert)

        # Add the htm16 IDs in bulk. Could have done it above as we iterate through the diaSource,
        # but the new C++ bulk code is 100 times faster than doing it one at a time.

    # Call on Cassandra
    try:
        cass_result = insert_cassandra_multi(alerts, cassandra_session)
        if cass_result:
            cass_futures += cass_result
    except Exception as e:
        log.error('ERROR in ingest/ingest: Cassandra insert failed' + str(e))
        return 0  # ingest batch failed

    for alert in alerts:
        # produce to kafka
        if producer is not None:
            try:
                s = json.dumps(alert)
                producer.produce(topic_out, json.dumps(alert))
            except Exception as e:
                log.error("ERROR in ingest/ingest: Kafka production failed for %s" % topic_out)
                log.error("ERROR:", e)
                sys.stdout.flush()
                return None   # ingest failed

    # Wait for image store futures to complete
    for future in image_futures:
        future.result()

    # Wait for cassandra futures to complete
    for future in cass_futures:
        future.result()

    return results

def run_ingest(args):
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

    alerts = []
    while ntotalalert < maxalert:
        if sigterm_raised:
            # clean shutdown - this should stop the consumer and commit offsets
            log.info("Stopping ingest")
            sys.stdout.flush()
            break

        msg = consumer.poll(timeout=5)

        # no messages available
        if msg is None:
            end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource)
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

        alerts.append(lsst_alert)
        nalert += 1
        ntotalalert += 1

        # Apply filter to alerts every 10th alert
        if nalert % 10 == 0:
            results = handle_alerts(alerts, image_store, producer, topic_out, cassandra_session)
            for (idiaSource,iforcedSource) in results:
                ndiaSource += idiaSource
                nforcedSource += iforcedSource
            alerts = []

        # every so often commit, flush, and update status
        if nalert >= 250:
            end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource)
            nalert = ndiaSource = nforcedSource = 0
            # check for lockfile
            if not os.path.isfile(settings.LOCKFILE):
                log.info('Lockfile not present')
                stop = True

    # if we exit this loop, clean up
    log.info('Shutting down')
    end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource)

    # shut down kafka consumer
    consumer.close()

    # shut down the cassandra cluster
    if cassandra_session:
        cluster.shutdown()

    # did we get any alerts
    if ntotalalert > 0: return 1
    else:               return 0

def end_batch(consumer, producer, ms, nalert, ndiaSource, nforcedSource):
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

if __name__ == "__main__":
    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("ingest")

    signal.signal(signal.SIGTERM, sigterm_handler)

    args = docopt(__doc__)
    rc = run_ingest(args)
    # rc=1, got alerts, more to come
    # rc=0, got no alerts
    sys.exit(rc)

