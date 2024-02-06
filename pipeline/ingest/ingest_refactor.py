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
import logging, lasairLogging

class ImageStore():
    """Class to wrap the cassandra and file system image stores and give them a
    common interface."""

    def __init__(self, log=None, image_store=None):
        if image_store is not None:
            # passing in an image_store instead of getting one is mostly to enable testing
            self.image_store = image_store
            return
        self.log = log
        fitsdir = getattr(settings, 'IMAGEFITS', None)
        if settings.USE_CUTOUTCASS:
            self.image_store = cutoutStore.cutoutStore()
            if self.image_store.session == None:
                self.image_store = None
        elif fitsdir and len(fitsdir) > 0:
            print(fitsdir)
            self.image_store = objectStore.objectStore(suffix='fits', fileroot=fitsdir)
        else:
            log.warn('ERROR in ingest: Cannot store cutouts. USE_CUTOUTCASS=%s' % settings.USE_CUTOUTCASS)
    
    def store_images(self, message, diaSourceId, imjd, diaObjectId):
        futures = []
        try:
            for cutoutType in ['cutoutDifference', 'cutoutTemplate']:
                if not cutoutType in message: 
                    continue
                content = message[cutoutType]
                cutoutId = '%d_%s' % (diaSourceId, cutoutType)
                # store may be cutouts or cephfs
                if settings.USE_CUTOUTCASS:
                    result = self.image_store.putCutoutAsync(cutoutId, imjd, diaObjectId, content)
                    futures.append(result)
                else:
                    self.image_store.putObject(cutoutId, imjd, content)
        except Exception as e:
            self.log.error('ERROR in ingest/store_images: ', e)
            raise e
        return futures


class Ingester():
    # We split the setup between the constructor and setup method in order to allow for
    # an ingester with custom connections to other components, e.g. for testing

    def __init__(self, topic_in, topic_out, group_id, maxalert, log=None, image_store=None, cassandra_session=None, producer=None, consumer=None):
        self.topic_in = topic_in
        self.topic_out = topic_out
        self.group_id = group_id
        self.maxalert = maxalert
        self.log = log
        self.image_store = image_store
        self.cassandra_session=cassandra_session
        self.producer = producer
        self.consumer = consumer
        self.pschema = None
        self.cluster = None

        # if we weren't given a log to use then create a default one
        if log:
            self.log = log
        else:
            lasairLogging.basicConfig(stream=sys.stdout, level=logging.INFO)
            self.log = lasairLogging.getLogger("ingest")

        # catch SIGTERM so that we can finish processing cleanly
        signal.signal(signal.SIGTERM, self._sigterm_handler)
        self.sigterm_raised = False
        
        # list of future objects for in-flight cassandra requests
        self.futures = []

    def setup(self):
        """Setup connections to Cassandra, Kafka, etc."""
        log = self.log

        # set up image store in Cassandra or shared file system
        if self.image_store is None:
            self.image_store = ImageStore()

        # connect to cassandra cluster for alerts (not cutouts)
        if self.cassandra_session is None:
            try:
                self.cluster = Cluster(settings.CASSANDRA_HEAD)
                self.cassandra_session = self.cluster.connect()
                self.cassandra_session.set_keyspace('lasair')
            except Exception as e:
                log.warn("ERROR in ingest/setup: Cannot connect to Cassandra", e)
                self.cassandra_session = None
                #TODO: are we OK with continuing or should we re-raise the exception?

        # set up kafka producer
        if self.producer is None:
            producer_conf = {
                'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
                'client.id': 'client-1',
            }
            self.producer = Producer(producer_conf)
            log.info('Producing to   %s' % settings.KAFKA_SERVER)
        
        # set up kafka consumer
        if self.consumer is None:
            log.info('Consuming from %s' % settings.KAFKA_SERVER)
            log.info('Topic_in       %s' % self.topic_in)
            log.info('Topic_out      %s' % self.topic_out)
            log.info('group_id       %s' % self.group_id)
            log.info('maxalert       %d' % self.maxalert)

            consumer_conf = {
                'bootstrap.servers'   : '%s' % settings.KAFKA_SERVER,
                'group.id'            : self.group_id,
                'enable.auto.commit'  : False,
                'default.topic.config': {'auto.offset.reset': 'earliest'},
                # wait twice wait time before forgetting me
                'max.poll.interval.ms': 50*settings.WAIT_TIME*1000,  
            }
    
            try:
                self.consumer = Consumer(consumer_conf)
                self.consumer.subscribe([self.topic_in])
            except Exception as e:
                log.error('ERROR in ingest/setup: Cannot connect to Kafka', e)
                raise e

        # read the schema
        with open(settings.SCHEMA) as f:
            schema = json.loads(f.read())
            self.pschema = fastavro.parse_schema(schema)
    
    def _sigterm_handler(self, signum, frame):
        """Handle SIGTERM by raising a flag that can be checked during the poll/process loop."""
        self.sigterm_raised = True
        self.log.debug("caught SIGTERM")

    @classmethod
    def _now(cls):
        """current UTC as string"""
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _insert_cassandra(self, alert):
        """Inset a single alert into cassandra.
        Returns a list of future objects."""
        result = self._insert_cassandra_multi([alert])
        if result:
            return result

    def _insert_cassandra_multi(self, alerts):
        """Insert a list of alerts into casssandra."""
        log = self.log
        if not self.cassandra_session:
            # if this is not set, then we are not doing cassandra
            log.debug("cassandra_session not set, skipping")
            return None
        diaObjects = []
        diaSourcesList = []
        forcedSourceOnDiaObjectsList = []
        for alert in alerts:
            diaObjects.append(alert['diaObject'])
            diaSourcesList += alert['diaSourcesList']
            forcedSourceOnDiaObjectsList += alert['forcedSourceOnDiaObjectsList']
        self.futures += executeLoadAsync(self.cassandra_session, 'DiaObjects', diaObjects)
        if len(diaSourcesList) > 0:
            self.futures += executeLoadAsync(self.cassandra_session, 'DiaSources', diaSourcesList)
        if len(forcedSourceOnDiaObjectsList) > 0:
            self.futures += executeLoadAsync(self.cassandra_session, 'ForcedSourceOnDiaObjects', forcedSourceOnDiaObjectsList)

    def _handle_alert(self, lsst_alert):
        """Handle a single alert"""
        return self._handle_alerts([lsst_alert])

    def _handle_alerts(self, lsst_alerts):
        """Handle a list of alerts.
        Store cutout images, write information to cassandra, and produce a kafka message.

        Args:
            lsst_alert:
            image_store:
            producer:
            topic_out:

        Returns: (number of diaSoucres, number of forced sources)
        """
        log = self.log
        nDiaSources = 0
        nForcedSources = 0

        alerts = []
        for lsst_alert in lsst_alerts:
            diaObject = lsst_alert['DiaObject']
            diaSourcesList = lsst_alert['DiaSourceList']
            forcedSourceOnDiaObjectsList = lsst_alert['ForcedSourceOnDiaObjectList']
            nDiaSources += len(diaSourcesList)
            nForcedSources += len(forcedSourceOnDiaObjectsList)

            # deal with images
            if self.image_store:
                try:
                    # get the MJD for the latest detection
                    lastSource = sorted(diaSourcesList, key=lambda x: x['midPointTai'], reverse=True)[0]
                    # ID for the latest detection, this is what the cutouts belong to
                    diaSourceId = lastSource['diaSourceId']
                    # MJD for storing images
                    imjd = int(lastSource['midPointTai'])
                    # objectID
                    diaObjectId = diaObject['diaObjectId']
                    # store the fits images
                    image_futures = self.image_store.store_images(lsst_alert, diaSourceId, imjd, diaObjectId)
                    self.futures += image_futures
                except IndexError:
                    # This will happen if the list of sources is empty
                    log.debug("No latest detection so not storing cutouts")

            # build the outgoing alerts
            alert = {
                'diaObject': diaObject,
                'diaSourcesList': diaSourcesList,
                'forcedSourceOnDiaObjectsList': forcedSourceOnDiaObjectsList,
            }
            alerts.append(alert)

        # Call on Cassandra
        if len(alerts) > 0:
            try:
                self._insert_cassandra_multi(alerts)
            except Exception as e:
                log.error('ERROR in ingest/handle_alerts: Cassandra insert failed' + str(e))
                raise e

        # produce to kafka
        for alert in alerts:
            if self.producer is not None:
                try:
                    s = json.dumps(alert)
                    self.producer.produce(self.topic_out, json.dumps(alert))
                except Exception as e:
                    log.error("ERROR in ingest/handle_alerts: Kafka production failed for %s" % self.topic_out)
                    log.error("ERROR:", e)
                    raise e

        return (nDiaSources, nForcedSources)

    def _end_batch(self, ms, nalert, ndiaSource, nforcedSource):
        log = self.log

        # wait for any in-flight cassandra requests to complete
        for future in self.futures:
            future.result()
        self.futures = []

        # if this is not flushed, it will run out of memory
        if self.producer is not None:
            self.producer.flush()

        # commit the alerts we have read
        self.consumer.commit()

        # update the status page
        nid  = date_nid.nid_now()
        ms.add({'today_alert':nalert, 'today_diaSource':ndiaSource}, nid)

        log.info('%s %d alerts %d diaSource %d forcedSource' % (self._now(), nalert, ndiaSource, nforcedSource))
        sys.stdout.flush()

    def _poll(self, n):
        """Poll for n alerts."""
        alerts = []
        while len(alerts) < n:
            if self.sigterm_raised:
                # clean shutdown - this should stop the consumer and commit offsets
                log.debug("Stopping polling for alerts")
                break
            msg = self.consumer.poll(timeout=5)
            # no more messages available
            if msg is None:
                break
            # read the avro contents
            bytes_io = io.BytesIO(msg.value())
            lsst_alert = fastavro.schemaless_reader(bytes_io, self.pschema)
            alerts.append(lsst_alert)
        return alerts

    def run(self):
        """run."""
        log = self.log
    
        # TODO: put this in a config file?
        batch_size = 100
        mini_batch_size = 10

        # setup connections to Kafka, Cassandra, etc.
        self.setup()
    
        nalert = 0        # number not yet send to manage_status
        ndiaSource = 0    # number not yet send to manage_status
        nforcedSource = 0    # number not yet send to manage_status
        ntotalalert = 0   # number since this program started
        log.info('INGEST starts %s' % self._now())
    
        # put status on Lasair web page
        ms = manage_status.manage_status(settings.SYSTEM_STATUS)
    
        while ntotalalert < self.maxalert:
            if self.sigterm_raised:
                # clean shutdown - this should stop the consumer and commit offsets
                log.info("Stopping ingest")
                break

            # poll for alerts
            alerts = self._poll(mini_batch_size)
            n = len(alerts)
            nalert += n
            ntotalalert += n

            # process alerts
            (idiaSource,iforcedSource) = self._handle_alerts(alerts)
            ndiaSource += idiaSource
            nforcedSource += iforcedSource
           
            # partial alert batch case
            if n < mini_batch_size:
                self._end_batch(ms, nalert, ndiaSource, nforcedSource)
                nalert = ndiaSource = nforcedSource = 0
                log.debug('no more messages ... sleeping %d seconds' % settings.WAIT_TIME)
                time.sleep(settings.WAIT_TIME)
    
            # every so often commit, flush, and update status
            if nalert >= batch_size:
                self._end_batch(ms, nalert, ndiaSource, nforcedSource)
                nalert = ndiaSource = nforcedSource = 0
    
        # if we exit this loop, clean up
        log.info('Shutting down')
    
        self._end_batch(ms, nalert, ndiaSource, nforcedSource)
    
        # shut down kafka consumer
        self.consumer.close()
    
        # shut down the cassandra cluster
        if self.cassandra_session:
            self.cluster.shutdown()
    
        # did we get any alerts
        if ntotalalert > 0: return 1
        else:               return 0

def run_ingest(args):
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


    ingester = Ingester(topic_in, topic_out, group_id, maxalert)
    return ingester.run()

if __name__ == "__main__":
    args = docopt(__doc__)
    rc = run_ingest(args)
    # rc=1, got alerts, more to come
    # rc=0, got no alerts
    sys.exit(rc)

