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
              [--wait_time=TIME]
              [--nocutouts]

Options:
    --nprocess=NP      Number of processes to use [default:1]
    --maxalert=MAX     Number of alerts to process, default is from settings.
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, or
    --nid=NID          ZTF night number to use (default today)
    --topic_out=TOUT   Kafka topic for output [default:ztf_sherlock]
    --wait_time=TIME   Override default wait time (in seconds)
    --nocutouts        Do not attempt to save cutout images
"""

import sys
import json
from docopt import docopt
import datetime
from confluent_kafka import Consumer, Producer, KafkaError
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

from cassandra.cluster import Cluster, NoHostAvailable
from gkdbutils.ingesters.cassandra.ingestGenericDatabaseTable import executeLoadAsync
import time, json, io, fastavro, signal

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import manage_status, date_nid, slack_webhook
import cutoutStore
import logging, lasairLogging

class ImageStore:
    """Class to wrap the cassandra and file system image stores and give them a
    common interface."""

    def __init__(self, log=None, image_store=None):
        self.log = log
        if image_store is not None:
            # passing in an image_store instead of getting one is mostly to enable testing
            self.image_store = image_store
            return
        self.image_store = cutoutStore.cutoutStore()
        if self.image_store.session is None:
            self.image_store = None
            log.error('ERROR: Cannot store cutouts')
            sys.exit(1)

    def store_images(self, message, diaSourceId, diaObjectId):
        futures = []
        try:
            if self.image_store:
                for cutoutType in ['cutoutScience', 'cutoutDifference', 'cutoutTemplate']:
                    content = message.get(cutoutType)
                    if content:
                        cutoutId = '%d_%s' % (diaSourceId, cutoutType)
                        result = self.image_store.putCutoutAsync(cutoutId, diaObjectId, content)
                        for future in result:
                            futures.append({'future': future, 'msg': 'image_store.putCutoutAsync'})
            else:
                self.log.warning('WARNING: attempted to store images, but no image store set up')
        except Exception as e:
            self.log.error('ERROR in ingest/store_images: %s' % e)
            raise e
        return futures


class Ingester:
    # We split the setup between the constructor and setup method in order to allow for
    # an ingester with custom connections to other components, e.g. for testing

    def __init__(self, topic_in, topic_out, group_id, maxalert, nocutouts=False, log=None, image_store=None, cassandra_session=None, producer=None, consumer=None, ms=None):
        self.topic_in = topic_in
        self.topic_out = topic_out
        self.group_id = group_id
        self.maxalert = maxalert
        self.nocutouts = nocutouts
        self.log = log
        self.image_store = image_store
        self.cassandra_session=cassandra_session
        self.producer = producer
        self.consumer = consumer
        self.pschema = None
        self.cluster = None
        self.timers = {}
        
        self.wait_time = getattr(settings, 'WAIT_TIME', 60)

        # set up timers
        for name in ['icutout', 'icassandra', 'ifuture', 'ikconsume', 'ikproduce', 'itotal']:
            self.timers[name] = manage_status.timer(name)

        # if we weren't given a log to use then create a default one
        if log:
            self.log = log
        else:
            lasairLogging.basicConfig(stream=sys.stdout, level=logging.INFO)
            self.log = lasairLogging.getLogger("ingest")

        # put status on Lasair web page
        if ms:
            self.ms = ms
        else:
            self.ms = manage_status.manage_status(log=self.log)
    
        # catch SIGTERM so that we can finish processing cleanly
        signal.signal(signal.SIGTERM, self._sigterm_handler)
        self.sigterm_raised = False
        
        # list of future objects for in-flight cassandra requests
        self.futures = []

    def setup_cassandra(self):
        """Setup connections to Cassandra, Kafka, etc."""
        log = self.log

        # set up image store in Cassandra or shared file system
        if self.image_store is None and not self.nocutouts:
            self.image_store = ImageStore(log=self.log)

        # connect to cassandra cluster for alerts (not cutouts)
        if self.cassandra_session is None:
            try:
                self.cluster = Cluster(settings.CASSANDRA_HEAD)
                self.cassandra_session = self.cluster.connect()
                self.cassandra_session.set_keyspace('lasair')
                self.cassandra_session.default_timeout = 90
            except Exception as e:
                log.warning("ERROR in ingest/setup: Cannot connect to Cassandra", e)
                self.cassandra_session = None
                raise e

    def setup_producer(self):
        # set up kafka producer
        log = self.log
        if self.producer is None:
            producer_conf = {
                'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
                'client.id': 'client-1',
                'message.max.bytes': 10000000
            }
            self.producer = Producer(producer_conf)
            log.info('Producing to   %s' % settings.KAFKA_SERVER)
        
    def setup_consumer(self):
        # set up kafka consumer
        log = self.log
        if self.consumer is None:
            log.info('Consuming from %s' % settings.KAFKA_SERVER)
            log.info('Topic_in       %s' % self.topic_in)
            log.info('Topic_out      %s' % self.topic_out)
            log.info('group_id       %s' % self.group_id)
            log.info('maxalert       %d' % self.maxalert)

            sr_client = SchemaRegistryClient({"url": settings.SCHEMA_REG_URL})
            deserializer = AvroDeserializer(sr_client)
            consumer_conf = {
                'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
                'group.id': self.group_id,
                'enable.auto.commit': False,
                'default.topic.config': {'auto.offset.reset': 'earliest'},
                # wait twice wait time before forgetting me
                'max.poll.interval.ms': 50*self.wait_time*1000,  
                "value.deserializer": deserializer,
            }
    
            try:
                self.consumer = DeserializingConsumer(consumer_conf)   # hack
                self.consumer.subscribe([self.topic_in])
            except Exception as e:
                log.error('ERROR in ingest/setup: Cannot connect to Kafka', e)
                raise e

    def setup(self):
        self.setup_consumer()
        self.setup_producer()
        self.setup_cassandra()

    # end of class Ingester
    
    def _sigterm_handler(self, signum, frame):
        """Handle SIGTERM by raising a flag that can be checked during the poll/process loop."""
        self.sigterm_raised = True
        self.log.debug("caught SIGTERM")

    @classmethod
    def _now(cls):
        """current UTC as string"""
        return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _handle_alerts(self, lsst_alerts):
        """Handle a list of alerts.
        Store cutout images, write information to cassandra, and produce a kafka message.

        Args:
            lsst_alerts:

        Returns: (nObject, nNoDiaObject, nSSObject, nDiaSources, nDiaSourcesDB, nForcedSources, nForcedSourcesDB)
        """
        log = self.log
        nDiaObject       = 0
        nNoDiaObject     = 0
        nSSObject        = 0
        nDiaSources      = 0
        nDiaSourcesDB    = 0
        nForcedSources   = 0
        nForcedSourcesDB = 0

        alerts = []    # pushed to kafka, sherlock, filters etc
        alertsDB = []  # put into cassandra

        for lsst_alert in lsst_alerts:
#            observation_reason = lsst_alert.get('observation_reason', '')
#            target_name        = lsst_alert.get('target_name', '')

            diaSourcesList = [lsst_alert['diaSource']]
            # sort the diaSources, newest first
            if 'prvDiaSources' in lsst_alert and lsst_alert['prvDiaSources']:
                diaSourcesList = diaSourcesList + lsst_alert['prvDiaSources']
            nDiaSources += len(diaSourcesList)
            diaSourcesList = sorted(diaSourcesList, key=lambda x: x['midpointMjdTai'], reverse=True)

            diaObject = lsst_alert.get('diaObject', None)
            ssObject  = lsst_alert.get('ssObject', None)

            # deal with images
            if not self.nocutouts and self.image_store.image_store:
                try:
                    # get the MJD for the latest detection
                    lastSource = diaSourcesList[0]
                    # ID for the latest detection, this is what the cutouts belong to
                    diaSourceId = lastSource['diaSourceId']
                    # objectID
                    if diaObject:
                        objectId = diaObject['diaObjectId']
                    elif ssObject:
                        objectId = ssObject['ssObjectId']
                    else:
                        objectId = 0

                    # store the fits images
                    self.timers['icutout'].on()
                    image_futures = self.image_store.store_images(lsst_alert, diaSourceId, objectId)
                    self.timers['icutout'].off()
                    self.futures += image_futures
                except IndexError:
                    # This will happen if the list of sources is empty
                    log.debug("No latest detection so not storing cutouts")

            if not diaObject:   # solar system
#                print('ss alert')
                ssSource = lsst_alert['ssSource']
                MPCORB   = lsst_alert['MPCORB']
                if ssObject:
                    nSSObject += 1
                nNoDiaObject += 1
                alertDB = {
                    'diaSourcesList': diaSourcesList,
                    'ssObject'      : ssObject,
                    'ssSource'      : ssSource,
                    'MPCORB'        : MPCORB,
                }
                diaSource = diaSourcesList[0]
                if 'dec' in diaSource:
                    diaSource['decl'] = diaSource['dec']
                    del diaSource['dec']
                if ssSource['diaSourceId'] is None:
                    ssSource['diaSourceId'] = 0
                nDiaSources += 1
                alertsDB.append(alertDB)
                continue   # all done with this solar system alert

            diaObject = lsst_alert['diaObject']
#            print('==', diaObject['diaObjectId'])
            nDiaObject += 1

            if 'prvDiaForcedSources' in lsst_alert and lsst_alert['prvDiaForcedSources']:
                diaForcedSourcesList = lsst_alert['prvDiaForcedSources']
            else:
                diaForcedSourcesList = []
            nForcedSources += len(diaForcedSourcesList)

            if 'prvDiaNondetectionLimits' in lsst_alert and lsst_alert['prvDiaNondetectionLimits']:
                diaNondetectionLimitsList = lsst_alert['prvDiaNondetectionLimits']
            else:
                diaNondetectionLimitsList = []

            # change dec to decl so MySQL doesnt get confused
            if 'dec' in diaObject:
                diaObject['decl'] = diaObject['dec']
                del diaObject['dec']

            for diaSource in diaSourcesList:
#                print('--', diaSource['diaSourceId'])
                if 'dec' in diaSource:
                    diaSource['decl'] = diaSource['dec']
                    del diaSource['dec']
            for diaForcedSource in diaForcedSourcesList:
                if 'dec' in diaForcedSource:
                    diaForcedSource['decl'] = diaForcedSource['dec']
                    del diaForcedSource['dec']

            # sort the diaForcedSources, newest first
            diaForcedSourcesList = sorted(diaForcedSourcesList, key=lambda x: x['midpointMjdTai'], reverse=True)

            diaSourcesListDB            = diaSourcesList
            diaForcedSourcesListDB      = diaForcedSourcesList
            diaNondetectionLimitsListDB = diaNondetectionLimitsList

            # build the subset of the diaSources and diaForcedSources that do into Cassandra
            # if more than 4 diaSources, take only diaForcedSources after fourth diaSource
            nds = settings.N_DIASOURCES_DB
            if len(diaSourcesList) < nds:
                diaSourcesListDB            = diaSourcesList
                diaForcedSourcesListDB      = diaForcedSourcesList
                diaNondetectionLimitsListDB = diaNondetectionLimitsList
            else:
                diaSourcesListDB = diaSourcesList[:nds]
                fourthMJD = diaSourcesList[nds-1]['midpointMjdTai']

                if len(diaForcedSourcesList) > 0:
                    for i in range(len(diaForcedSourcesList)):
                        if diaForcedSourcesList[i]['midpointMjdTai'] < fourthMJD:
                            break
                    diaForcedSourcesListDB = diaForcedSourcesList[:i]
                else:
                    diaForcedSourcesListDB = []
    
                if len(diaNondetectionLimitsList) > 0:
                    for i in range(len(diaNondetectionLimitsList)):
                        if diaNondetectionLimitsList[i]['midpointMjdTai'] < fourthMJD:
                            break
                    diaNondetectionLimitsListDB = diaNondetectionLimitsList[:i]
                else:
                    diaNondetectionLimitsListDB = []

            alert = {
                'diaObject': diaObject,
                'diaSourcesList': diaSourcesList,
                'diaForcedSourcesList': diaForcedSourcesList,
                'diaNondetectionLimitsList': diaNondetectionLimitsList,
            }
            alerts.append(alert)

            alertDB = {
                'diaObject': diaObject,
                'diaSourcesList': diaSourcesListDB,
                'diaForcedSourcesList': diaForcedSourcesListDB,
                'diaNondetectionLimitsList': diaNondetectionLimitsListDB,
            }
            alertsDB.append(alertDB)

            nDiaSourcesDB += len(diaSourcesListDB)
            nForcedSourcesDB += len(diaForcedSourcesListDB)

            # end of loop over lsst_alerts #####

        # Call on Cassandra
        # both diaObjects and ssObjects go in
        if len(alertsDB) > 0:
            try:
                self.timers['icassandra'].on()
                self._insert_cassandra_multi(alertsDB)
                self.timers['icassandra'].off()
            except Exception as e:
                log.error('ERROR in ingest/handle_alerts: Cassandra insert failed' + str(e))
                raise e

        # produce to kafka
        self.timers['ikproduce'].on()
        for alert in alerts:
            if self.producer is not None:
                try:
                    s = json.dumps(alert)
                    self.producer.produce(self.topic_out, json.dumps(alert))
                except Exception as e:
                    log.error("ERROR in ingest/handle_alerts: Kafka production failed for %s" % self.topic_out)
                    log.error("ERROR:", e)
                    raise e
        self.timers['ikproduce'].off()

        return (nDiaObject, nNoDiaObject, nSSObject, nDiaSources, nDiaSourcesDB, nForcedSources, nForcedSourcesDB)

    def _insert_cassandra(self, alert):
        """Inset a single alert into cassandra.
        Returns a list of future objects."""
        return self._insert_cassandra_multi([alert])

    def _insert_cassandra_multi(self, alerts):
        """Insert a list of alerts into casssandra."""
        log = self.log
        if not self.cassandra_session:
            # if this is not set, then we are not doing cassandra
            log.debug("cassandra_session not set, skipping")
            return None
        diaObjects                = []
        diaSourcesList            = []
        diaForcedSourcesList      = []
        diaNondetectionLimitsList = []
        ssObjects                 = []
        ssSources                 = []
        MPCORBs                   = []
        for alert in alerts:
            diaSourcesList += alert['diaSourcesList']

            if 'diaObject' in alert:
                diaObjects.append(alert['diaObject'])
                diaForcedSourcesList += alert['diaForcedSourcesList']
                diaNondetectionLimitsList += alert['diaNondetectionLimitsList']

            if 'ssSource' in alert and alert['ssSource']:
                ssSources.append(alert['ssSource'])
                MPCORBs.append(alert['MPCORB'])
            if 'ssObject' in alert and alert['ssObject']:
                ssObjects += alert['ssObject']

#        print(len(diaObjects), len(diaSourcesList), len(diaForcedSourcesList), len(diaNondetectionLimitsList), len(ssObjects))

        if len(diaObjects) > 0:
            for future in executeLoadAsync(self.cassandra_session, 'diaObjects', diaObjects):
                self.futures.append({'future': future, 'msg': 'executeLoadAsync diaObjects'})

        if len(diaSourcesList) > 0:
            for future in executeLoadAsync(self.cassandra_session, 'diaSources', diaSourcesList):
                self.futures.append({'future': future, 'msg': 'executeLoadAsync diaSources'})

        if len(diaForcedSourcesList) > 0:
            for future in executeLoadAsync(self.cassandra_session, 'diaForcedSources', diaForcedSourcesList):
                self.futures.append({'future': future, 'msg': 'executeLoadAsync diaForcedSources'})

        if len(diaNondetectionLimitsList) > 0:
            for future in executeLoadAsync(self.cassandra_session, 'diaNondetectionLimits', diaNondetectionLimitsList):
                self.futures.append({'future': future, 'msg': 'executeLoadAsync diaNondetectionLimits'})

        if len(ssObjects) > 0:
            for future in executeLoadAsync(self.cassandra_session, 'ssObjects', ssObjects):
                self.futures.append({'future': future, 'msg': 'executeLoadAsync ssObjects'})

        if len(ssSources) > 0:
            for future in executeLoadAsync(self.cassandra_session, 'ssSources', ssSources):
                self.futures.append({'future': future, 'msg': 'executeLoadAsync ssSources'})

        if len(MPCORBs) > 0:
            for future in executeLoadAsync(self.cassandra_session, 'MPCORBs', MPCORBs):
                self.futures.append({'future': future, 'msg': 'executeLoadAsync MPCORBs'})

    def _handle_alert(self, lsst_alert):
        """Handle a single alert"""
        return self._handle_alerts([lsst_alert])

    def _end_batch(self, nAlert, nDiaObject, nNoDiaObject, nSSObject, nDiaSource, nDiaSourceDB, nDiaForcedSource, nDiaForcedSourceDB):
        log = self.log

        # wait for any in-flight cassandra requests to complete
        self.timers['ifuture'].on()
        for future in self.futures:
            try:
                future['future'].result()
            except Exception as e:
                log.error("ERROR getting future result for {}".format(future['msg']))
                raise e
        self.timers['ifuture'].off()
        self.futures = []

        # if this is not flushed, it will run out of memory
        if self.producer is not None:
            self.producer.flush()

        self.timers['ikconsume'].on()
        # commit the alerts we have read
        if self.consumer:
            self.consumer.commit()
        self.timers['ikconsume'].off()

        # update the status page
        nid = date_nid.nid_now()
        self.ms.add({
            'today_alert':nAlert, 
            'diaObject'        : nDiaObject,
            'noDiaObject'      : nNoDiaObject,
            'ssObject'         : nSSObject,
            'diaSource'        : nDiaSource,
            'diaSourceDB'      : nDiaSourceDB,
            'diaForcedSource'  : nDiaForcedSource,
            'diaForcedSourceDB': nDiaForcedSourceDB
        }, nid)
        for name,td in self.timers.items():
            td.add2ms(self.ms, nid)

        log.info('%s %d alerts %d diaSource %d forcedSource %d noObject' % (self._now(), nAlert, nDiaSource, nDiaForcedSource, nNoDiaObject))
        sys.stdout.flush()

    def _poll(self, n):
        """Poll for n alerts."""
        log = self.log
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
            if msg.error():
                log.error('ERROR in ingest/poll: ' +  str(msg.error()))
                break
            lsst_alert = msg.value()
            alerts.append(lsst_alert)
        return alerts

    def run(self):
        """Run ingester. Return the total number of alerts ingested."""
        log = self.log
    
        batch_size = getattr(settings, 'INGEST_BATCH_SIZE', 200)
        mini_batch_size = getattr(settings, 'INGEST_MINI_BATCH_SIZE', 10)

        # setup connections to Kafka, Cassandra, etc.
        self.setup_cassandra()
        self.setup_consumer()
        self.setup_producer()
    
        nAlert = 0        # number not yet send to manage_status
        nTotalAlert = 0   # number since this program started
        nDiaObject = 0
        nNoDiaObject = 0
        nSSObject = 0
        nDiaSource = 0
        nDiaSourceDB = 0
        nDiaForcedSource = 0
        nDiaForcedSourceDB = 0
        log.info('INGEST starts %s' % self._now())
    
        n_remaining = self.maxalert
        self.timers['itotal'].on()
        while n_remaining > 0:
            n_remaining = self.maxalert - nTotalAlert
            if n_remaining < mini_batch_size:
                mini_batch_size = n_remaining

            # clean shutdown - this should stop the consumer and commit offsets
            if self.sigterm_raised:
                log.info("Stopping ingest")
                break

            # poll for alerts
            self.timers['ikconsume'].on()
            alerts = self._poll(mini_batch_size)
            self.timers['ikconsume'].off()
            n = len(alerts)
            nAlert += n
            nTotalAlert += n

            # process alerts
            (iDiaObject, iNoDiaObject, iSSObject, iDiaSource, iDiaSourceDB, iDiaForcedSource, iDiaForcedSourceDB) = self._handle_alerts(alerts)
            nDiaObject += iDiaObject
            nNoDiaObject += iNoDiaObject
            nSSObject += iSSObject
            nDiaSource += iDiaSource
            nDiaSourceDB += iDiaSourceDB
            nDiaForcedSource += iDiaForcedSource
            nDiaForcedSourceDB += iDiaForcedSourceDB

            # partial alert batch case
            if n < mini_batch_size:
                self._end_batch(nAlert, nDiaObject, nNoDiaObject, nSSObject, nDiaSource, nDiaSourceDB, nDiaForcedSource, nDiaForcedSourceDB)
                nDiaObject = nNoDiaObject = nSSObject = 0
                nDiaSource = nDiaForcedSource = 0
                nDiaSourceDB = nDiaForcedSourceDB = 0
                log.debug('no more messages ... sleeping %d seconds' % self.wait_time)
                self.timers['itotal'].off()
                time.sleep(self.wait_time)
                self.timers['itotal'].on()
    
            # every so often commit, flush, and update status
            if nAlert >= batch_size:
                self._end_batch(nAlert, nDiaObject, nNoDiaObject, nSSObject, nDiaSource, nDiaSourceDB, nDiaForcedSource, nDiaForcedSourceDB)
                nDiaObject = nNoDiaObject = nSSObject = 0
                nAlert = nDiaSource = nDiaForcedSource = 0
                nDiaSourceDB = nDiaForcedSourceDB = 0
    
        self.timers['itotal'].off()

        # if we exit this loop, clean up
        log.info('Shutting down')
    
        self._end_batch(nAlert, nDiaObject, nNoDiaObject, nSSObject, nDiaSource, nDiaSourceDB, nDiaForcedSource, nDiaForcedSourceDB)
    
        # shut down kafka consumer
        self.consumer.close()
    
        # shut down the cassandra cluster
        if self.cassandra_session:
            self.cluster.shutdown()

        return nTotalAlert

def run_ingest(args, log=None):
    if args.get('--topic_in'):
        topic_in = args['--topic_in']
    else:
        topic_in = 'lsst-alerts-v9.0'

    topic_out = args.get('--topic_out') or 'ztf_ingest'
    group_id = args.get('--group_id') or settings.KAFKA_GROUPID
    maxalert = int(args.get('--maxalert') or sys.maxsize)  # largest possible integer
    nocutouts = args.get('--nocutouts', False)

    ingester = Ingester(topic_in, topic_out, group_id, maxalert, nocutouts, log=log)

    if args.get('--wait_time'):
        ingester.wait_time = int(args['--wait_time'])

    return ingester.run()


if __name__ == "__main__":
    args = docopt(__doc__)
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("ingest")
    rc = run_ingest(args, log)
    # rc=1, got alerts, more to come
    # rc=0, got no alerts
    print(f"Ingested {rc} total alerts")
    sys.exit(0)

