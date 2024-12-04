"""
The core filter module. Usually run as a service using filter_runner, but can also be run from the command line.

Usage:
    ingest.py [--maxalert=MAX]
              [--maxbatch=MAX]
              [--maxtotal=MAX]
              [--group_id=GID]
              [--topic_in=TIN]
              [--local_db=NAME]
              [--send_email=BOOL]
              [--send_kafka=BOOL]
              [--transfer=BOOL]
              [--stats=BOOL]
              [--wait_time=TIME]

Options:
    --maxalert=MAX     Number of alerts to process per batch, default is defined in settings.KAFKA_MAXALERTS
    --maxbatch=MAX     Maximum number of batches to process, default is unlimited
    --maxtotal=MAX     Maximum total alerts to process, default is unlimited
    --group_id=GID     Group ID for kafka, default is defined in settings.KAFKA_GROUPID
    --topic_in=TIN     Kafka topic to use [default: ztf_sherlock]
    --local_db=NAME    Name of local database to use [default: ztf]
    --send_email=BOOL  Send email [default: True]
    --send_kafka=BOOL  Send kafka [default: True]
    --transfer=BOOL    Transfer results to main [default: True]
    --stats=BOOL       Write stats [default: True]
    --wait_time=TIME   Override default wait time (in seconds)
"""

import os
import sys
import time
import signal
import json
import tempfile
import math
from typing import Union

import requests
import urllib
import urllib.parse
import numbers
import confluent_kafka
from datetime import datetime
from docopt import docopt

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import date_nid
import db_connect
import manage_status
import lasairLogging
import logging
import filters
import watchlists
import watchmaps
import mmagw

sys.path.append('../../common/schema/lasair_schema')
from features.FeatureGroup import FeatureGroup

sys.path.append('features/BBB')

def now():
    return datetime.utcnow().strftime("%H:%M:%S")


class Filter:
    """Filter orchestrates the filter pipeline stage.
    """

    def __init__(self,
                 topic_in: str = 'ztf_sherlock',
                 group_id: str = settings.KAFKA_GROUPID,
                 maxalert: (Union[int, str]) = settings.KAFKA_MAXALERTS,
                 local_db: str = None,
                 send_email: bool = True,
                 send_kafka: bool = True,
                 transfer: bool = True,
                 stats: bool = True,
                 log=None):
        self.topic_in = topic_in
        self.group_id = group_id
        self.maxalert = int(maxalert)
        self.local_db = local_db or 'ztf'
        self.send_email = send_email
        self.send_kafka = send_kafka
        self.transfer = transfer
        self.stats = stats

        self.consumer = None
        self.database = None

        self.log = log or lasairLogging.getLogger("filter")
        self.log.info('Topic_in=%s, group_id=%s, maxalert=%d' % (self.topic_in, self.group_id, self.maxalert))

        # catch SIGTERM so that we can finish processing cleanly
        self.prv_sigterm_handler = signal.signal(signal.SIGTERM, self._sigterm_handler)
        self.sigterm_raised = False

    def setup(self):
        """Set up connections to Kafka, database, etc. if not already done. It is safe to call this multiple
        times. We do this separately from __init__ mostly to facilitate testing."""

        # set up the Kafka consumer now
        if not self.consumer:
            self.consumer = self.make_kafka_consumer()

        # set up the link to the local database
        if not self.database or not self.database.is_connected():
            try:
                self.database = db_connect.local(self.local_db)
            except Exception as e:
                self.log.error('ERROR in Filter: cannot connect to local database' + str(e))

    def _sigterm_handler(self, signum, frame):
        """Handle SIGTERM by raising a flag that can be checked during the poll/process loop.
        """
        self.sigterm_raised = True
        self.log.debug("caught SIGTERM")
        # if we have already set a non-default handler then call that too
        if self.prv_sigterm_handler is not signal.SIG_DFL and not None:
            self.prv_sigterm_handler(signum, frame)

    def execute_query(self, query: str):
        """ execute_query: run a query and close it, and compalin to slack if failure.
        """
        try:
            cursor = self.database.cursor(buffered=True)
            cursor.execute(query)
            cursor.close()
            self.database.commit()
        except Exception as e:
            self.log.error('ERROR filter/execute_query: %s' % str(e))
            self.log.info(query)
            raise

    def truncate_local_database(self):
        """ Truncate all the tables in the local database.
        """
        self.execute_query('TRUNCATE TABLE objects')
        self.execute_query('TRUNCATE TABLE sherlock_classifications')
        self.execute_query('TRUNCATE TABLE watchlist_hits')
        self.execute_query('TRUNCATE TABLE area_hits')

    def make_kafka_consumer(self):
        """ Make a kafka consumer.
        """
        conf = {
            'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
            'enable.auto.commit': False,  # require explicit commit!
            'group.id': self.group_id,
            'max.poll.interval.ms': 20 * 60 * 1000,  # 20 minute timeout in case queries take time
            'default.topic.config': {
                'auto.offset.reset': 'earliest'
            }
        }
        self.log.info(str(conf))
        self.log.info('Topic in = %s' % self.topic_in)
        try:
            consumer = confluent_kafka.Consumer(conf)
            consumer.subscribe([self.topic_in])
            return consumer
        except Exception as e:
            self.log.error('ERROR cannot connect to kafka' + str(e))

    @staticmethod
    def create_insert_sherlock(ann: dict):
        """create_insert_sherlock.
        Makes the insert query for the sherlock classification

        Args:
            ann:
        """
        # all the sherlock attrs that we want for the database
        attrs = [
            "classification",
            "diaObjectId",
            "association_type",
            "catalogue_table_name",
            "catalogue_object_id",
            "catalogue_object_type",
            "raDeg",
            "decDeg",
            "separationArcsec",
            "northSeparationArcsec",
            "eastSeparationArcsec",
            "physical_separation_kpc",
            "direct_distance",
            "distance",
            "z",
            "photoZ",
            "photoZErr",
            "Mag",
            "MagFilter",
            "MagErr",
            "classificationReliability",
            "major_axis_arcsec",
            "annotator",
            "additional_output",
            "description",
            "summary",
        ]
        sets = {}
        for key in attrs:
            sets[key] = None
        for key, value in ann.items():
            if key in attrs and value:
                sets[key] = value
        if 'description' in attrs and 'description' not in ann:
            sets['description'] = 'no description'
        # Build the query
        query_list = []
        query = 'REPLACE INTO sherlock_classifications SET '
        for key, value in sets.items():
            if value is None:
                query_list.append(key + '=NULL')
            else:
                query_list.append(key + '=' + "'" + str(value).replace("'", '') + "'")
        query += ',\n'.join(query_list)
        return query

    @staticmethod
    def create_insert_query(alert: dict):
        """create_insert_query.
        Creates an insert sql statement for building the object and
        a query for inserting it.

        Args:
            alert:
        """

        lasair_features = FeatureGroup.run_all(alert)
        if not lasair_features:
            return None

        # Make the query
        query_list = []
        query = 'REPLACE INTO objects SET '
        for key, value in lasair_features.items():
            if not value:
                query_list.append(key + '=NULL')
            elif isinstance(value, numbers.Number) and math.isnan(value):
                query_list.append(key + '=NULL')
            elif isinstance(value, str):
                query_list.append(key + '="' + str(value) + '"')
            else:
                query_list.append(key + '=' + str(value))
        query += ',\n'.join(query_list)
        return query

    def handle_alert(self, alert: dict):
        """alert_filter: handle a single alert.
        """
        # Filter to apply to each alert.
        diaObjectId = alert['diaObject']['diaObjectId']

        # really not interested in alerts that have no detections!
        if len(alert['diaSourcesList']) == 0:
            return 0

        # build the insert query for this object.
        # if not wanted, returns 0
        query = Filter.create_insert_query(alert)
        if not query:
            return 0
        self.execute_query(query)

        # now ingest the sherlock_classifications
        if 'annotations' in alert:
            annotations = alert['annotations']
            if 'sherlock' in annotations:
                for ann in annotations['sherlock']:
                    if "transient_object_id" in ann:
                        ann.pop('transient_object_id')
                    ann['diaObjectId'] = diaObjectId
                    query = Filter.create_insert_sherlock(ann)
                    self.execute_query(query)
        return 1

    def consume_alerts(self):
        """Consume a batch of alerts from Kafka.
        """
        nalert_in = nalert_out = 0
        startt = time.time()
        errors = 0

        while nalert_in < self.maxalert:
            if self.sigterm_raised:
                # clean shutdown - stop the consumer
                self.log.info("Caught SIGTERM, aborting.")
                break

            # Here we get the next alert by kafka
            msg = self.consumer.poll(timeout=5)
            if msg is None:
                print('message is null')
                break
            if msg.error():
                self.log.error("ERROR polling Kafka: " + str(msg.error()))
                errors += 1
                if errors > 100:
                    break
                continue
            if msg.value() is None:
                print('message value is null')
                continue
            # Apply filter to each alert
            alert = json.loads(msg.value())
            nalert_in += 1
#            print(json.dumps(alert, indent=2))  ##############
            d = self.handle_alert(alert)
            nalert_out += d

            if nalert_in % 1000 == 0:
                self.log.info('nalert_in %d nalert_out  %d time %.1f' % \
                              (nalert_in, nalert_out, time.time() - startt))
                sys.stdout.flush()
                # refresh the database every 1000 alerts
                # make sure everything is committed
                self.database.commit()

        self.log.info('finished %d in, %d out' % (nalert_in, nalert_out))

        if self.stats:
            ms = manage_status.manage_status()
            nid = date_nid.nid_now()
            ms.add({
                'today_filter': nalert_in,
                'today_filter_out': nalert_out,
            }, nid)

        return nalert_out

    def transfer_to_main(self):
        """ Transfer the local database to the main database.
        """
        cmd = 'sudo --non-interactive rm /data/mysql/*.txt'
        os.system(cmd)

        tablelist = [
            'objects',
            'sherlock_classifications',
            'watchlist_hits',
            'area_hits',
            'mma_area_hits',
        ]

        # Make a CSV file for each local table
        for table in tablelist:
            query = """
                SELECT * FROM %s INTO OUTFILE '/data/mysql/%s.txt'
                FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n';
            """ % (table, table)

            try:
                self.execute_query(query)
            except:
                self.log.error('ERROR in filter/transfer_to_main: cannot build CSV from local database')
                return False

        # Transmit the CSV files to the main database and ingest them
        try:
            main_database = db_connect.remote(allow_infile=True)
        except Exception as e:
            self.log.error('ERROR filter/transfer_to_main: %s' % str(e))
            return False

        commit = True
        for table in tablelist:
            sql  = "LOAD DATA LOCAL INFILE '/data/mysql/%s.txt' " % table
            sql += "REPLACE INTO TABLE %s FIELDS TERMINATED BY ',' " % table
            sql += "ENCLOSED BY '\"' LINES TERMINATED BY '\n'"

            try:
                cursor = main_database.cursor(buffered=True)
                cursor.execute(sql)
                cursor.close()
                main_database.commit()
                self.log.info('%s ingested to main db' % table)
            except Exception as e:
                self.log.error('ERROR in filter/transfer_to_main: cannot push %s local to main database: %s' % (table, str(e)))
                commit = False
                break
        main_database.close()

        if commit:
            self.consumer.commit()
            self.log.info('Kafka committed for this batch')

        return commit

    def write_stats(self, timers: dict, nalerts: int):
        """ Write the statistics to lasair status and to prometheus.
        """
        if not self.stats:
            return

        ms = manage_status.manage_status()
        nid = date_nid.nid_now()
        d = Filter.batch_statistics()
        ms.set({
            'today_lsst': Filter.grafana_today(),
            'today_database': d['count'],
            'total_count': d['total_count'],
            'min_delay': d['since'],  # hours since most recent alert
            'nid': nid},
            nid)
        for name, td in timers.items():
            td.add2ms(ms, nid)

        if nalerts > 0:
            min_str = "{:d}".format(int(d['min_delay'] * 60))
            avg_str = "{:d}".format(int(d['avg_delay'] * 60))
            max_str = "{:d}".format(int(d['max_delay'] * 60))
        else:
            min_str = "NaN"
            avg_str = "NaN"
            max_str = "NaN"
        # t = int(1000*time.time())
        s = '#HELP lasair_alert_batch_lag Lasair alert batch lag stats\n'
        s += '#TYPE gauge\n'
        s += 'lasair_alert_batch_lag{type="min"} %s\n' % min_str
        s += 'lasair_alert_batch_lag{type="avg"} %s\n' % avg_str
        s += 'lasair_alert_batch_lag{type="max"} %s\n' % max_str
        try:
            filename = '/var/lib/prometheus/node-exporter/lasair.prom'
            f = open(filename, 'w')
            f.write(s)
            f.close()
        except:
            self.log.error("ERROR in filter/write_stats: Cannot open promethus export file %s" % filename)

    @staticmethod
    def batch_statistics():
        """How many objects updated since last midnight.
        """
        tainow = (time.time() / 86400 + 40587)
        midnight = math.floor(tainow - 0.5) + 0.5

        msl_main = db_connect.readonly()
        cursor = msl_main.cursor(buffered=True, dictionary=True)

        # objects modified since last midnight
        query = 'SELECT count(*) AS count FROM objects WHERE maxTai > %.1f' % midnight
        try:
            cursor.execute(query)
            for row in cursor:
                count = row['count']
                break
        except:
            count = -1

        # total number of objects
        query = 'SELECT count(*) AS total_count, mjdnow()-max(maxTai) AS since FROM objects'

        try:
            cursor.execute(query)
            for row in cursor:
                total_count = row['total_count']
                since = 24 * float(row['since'])
                break
        except:
            total_count = -1
            since = -1

        # statistics for most recent batch
        min_delay = -1
        avg_delay = -1
        max_delay = -1
        msl_local = db_connect.local()
        cursor = msl_local.cursor(buffered=True, dictionary=True)
        query = 'SELECT '
        query += 'tainow()-max(maxTai) AS min_delay, '
        query += 'tainow()-avg(maxTai) AS avg_delay, '
        query += 'tainow()-min(maxTai) AS max_delay '
        query += 'FROM objects'
        try:
            cursor.execute(query)
            for row in cursor:
                min_delay = 24 * 60 * float(row['min_delay'])  # minutes
                avg_delay = 24 * 60 * float(row['avg_delay'])  # minutes
                max_delay = 24 * 60 * float(row['max_delay'])  # minutes
                break
        except:
            pass

        return {
            'total_count': total_count,  # number of objects in database
            'count': count,  # number of objects updated since midnight
            'since': since,  # time since last object, hours
            'min_delay': min_delay,  # for grafana min delay in this batch, minutes
            'avg_delay': avg_delay,  # for grafana avg delay in this batch, minutes
            'max_delay': max_delay,  # for grafana max delay in this batch, minutes
        }

    @staticmethod
    def grafana_today():
        """How many objects reported today from LSST.
        """
        g = datetime.utcnow()
        date = '%4d%02d%02d' % (g.year, g.month, g.day)
        # do not have this for LSST yet
#        url = 'https://monitor.alerts.ztf.uw.edu/api/datasources/proxy/7/api/v1/query?query='
#        urltail = 'sum(kafka_log_log_value{ name="LogEndOffset" , night = "%s", program = "MSIP" }) ' \
#                  '- sum(kafka_log_log_value{ name="LogStartOffset", night = "%s", program="MSIP" })' % (
#                      date, date)

#        try:
#            urlquote = url + urllib.parse.quote(urltail)
#            resultjson = requests.get(urlquote,
#                                      auth=(settings.GRAFANA_USERNAME, settings.GRAFANA_PASSWORD))
#            result = json.loads(resultjson.text)
#            alertsstr = result['data']['result'][0]['value'][1]
#            today_candidates_ztf = int(alertsstr) // 4
#        except Exception as e:
#            log = lasairLogging.getLogger("filter")
#            log.info('Cannot parse grafana: %s' % str(e))
#            today_candidates_ztf = -1
        today_candidates_ztf = 0
        return today_candidates_ztf

    def run_batch(self):
        """Top level method that processes an alert batch.

        Does the following:
         - Consume alerts from Kafka
         - Run watchlists
         - Run watchmaps
         - Run user filters
         - Run annotation queries
         - Build CSV file
         - Transfer to main database"""

        self.setup()

        # set up the timers
        timers = {}
        for name in ['ffeatures', 'fwatchlist', 'fwatchmap', \
                'fmmagw', 'ffilters', 'ftransfer', 'ftotal']:
            timers[name] = manage_status.timer(name)

        self.truncate_local_database()

        timers['ftotal'].on()
        self.log.info('FILTER batch start %s' % now())
        self.log.info("Topic is %s" % self.topic_in)

        # consume the alerts from Kafka
        timers['ffeatures'].on()
        nalerts = self.consume_alerts()
        timers['ffeatures'].off()

        if nalerts > 0:
            # run the watchlists
            self.log.info('WATCHLIST start %s' % now())
            timers['fwatchlist'].on()
            nhits = watchlists.watchlists(self)
            timers['fwatchlist'].off()
            if nhits is not None:
                self.log.info('WATCHLISTS got %d' % nhits)
            else:
                self.log.error("ERROR in filter/watchlists")

            # run the watchmaps
            self.log.info('WATCHMAP start %s' % now())
            timers['fwatchmap'].on()
            nhits = watchmaps.watchmaps(self)
            timers['fwatchmap'].off()
            if nhits is not None:
                self.log.info('WATCHMAPS got %d' % nhits)
            else:
                self.log.error("ERROR in filter/watchmaps")

            # run the MMA/GW events
            self.log.info('MMA/GW start %s' % now())
            timers['fmmagw'].on()
            nhits = mmagw.mmagw(self)
            timers['fmmagw'].off()
            if nhits is not None:
                self.log.info('MMA/GW got %d' % nhits)
            else:
                self.log.error("ERROR in filter/mmagw")

            # run the user filters
            self.log.info('Filters start %s' % now())
            timers['ffilters'].on()
            ntotal = filters.filters(self)
            timers['ffilters'].off()
            if ntotal is not None:
                self.log.info('FILTERS got %d' % ntotal)
            else:
                self.log.error("ERROR in filter/filters")

            # run the annotation queries
            self.log.info('ANNOTATION FILTERS start %s' % now())
            ntotal = filters.fast_anotation_filters(self)
            if ntotal is not None:
                self.log.info('ANNOTATION FILTERS got %d' % ntotal)
            else:
                self.log.error("ERROR in filter/fast_annotation_filters")

            # build CSV file with local database and transfer to main
            if self.transfer:
                timers['ftransfer'].on()
                commit = self.transfer_to_main()
                timers['ftransfer'].off()
                self.log.info('Batch ended')
                if not commit:
                    self.log.info('Transfer to main failed, no commit')
                    time.sleep(600)
                    return 0

        # Write stats for the batch
        timers['ftotal'].off()
        self.write_stats(timers, nalerts)
        self.log.info('%d alerts processed\n' % nalerts)
        return nalerts


if __name__ == "__main__":
    #lasairLogging.basicConfig(stream=sys.stdout)
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()
    args = docopt(__doc__)

    topic_in = args.get('--topic_in') or 'ztf_sherlock'
    group_id = args.get('--group_id') or settings.KAFKA_GROUPID
    maxalert = int(args.get('--maxalert') or settings.KAFKA_MAXALERTS)
    maxbatch = int(args.get('--maxbatch') or -1)
    maxtotal = int(args.get('--maxtotal') or 0)
    local_db = args.get('--local_db')
    send_email = args.get('--send_email') in ['True', 'true', 'Yes', 'yes']
    send_kafka = args.get('--send_kafka') in ['True', 'true', 'Yes', 'yes']
    transfer = args.get('--transfer') in ['True', 'true', 'Yes', 'yes']
    stats = args.get('--stats') in ['True', 'true', 'Yes', 'yes']
    if args['--wait_time']:
        wait_time = int(args['--wait_time'])
    else: 
        wait_time = getattr(settings, 'WAIT_TIME', 60)

    fltr = Filter(topic_in=topic_in, group_id=group_id, maxalert=maxalert, local_db=local_db,
                  send_email=send_email, send_kafka=send_kafka, transfer=transfer, stats=stats)

    n_batch = 0
    total_alerts = 0
    while not fltr.sigterm_raised:
        n_alerts = fltr.run_batch()
        n_batch += 1
        total_alerts += n_alerts 
        if n_batch == maxbatch:
            log.info(f"Exiting after {n_batch} batches")
            sys.exit(0)
        if maxtotal and total_alerts >= maxtotal:
            log.info(f"Exiting after {total_alerts} alerts")
            sys.exit(0)
        if n_alerts == 0:  # process got no alerts, so sleep a few minutes
            log.info('Waiting for more alerts ....')
            time.sleep(wait_time)
