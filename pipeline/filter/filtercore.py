"""
The core filter module. Usually run as a service using filter_runner, but can also be run from the command line.

Usage:
    filtercore.py [--maxmessage=MAX]
                  [--maxalert=MAX]
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
                  [--verbose=BOOL]

Options:
    --maxmessage=MAX   Messages to process per batch, default is defined in settings.KAFKA_MAXALERTS
    --maxalert=MAX     Same as maxmessage
    --maxbatch=MAX     Maximum number of batches to process, default is unlimited
    --maxtotal=MAX     Maximum total alerts to process, default is unlimited
    --group_id=GID     Group ID for kafka, default is defined in settings.KAFKA_GROUPID
    --topic_in=TIN     Kafka topic to use [default: lsst_sherlock]
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
import confluent_kafka
import datetime
from docopt import docopt


sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import date_nid
import db_connect
import manage_status
import lasairLogging
import logging
from transfer import fetch_attrs, transfer_csv

sys.path.append('../../common/schema/' + settings.SCHEMA_VERSION)

def now():
    return datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")


class Filter:
    """Filter orchestrates the filter pipeline stage.
    """

    def __init__(self,
                 topic_in: str = 'lsst_sherlock',
                 group_id: str = settings.KAFKA_GROUPID,
                 maxmessage: (Union[int, str]) = settings.KAFKA_MAXALERTS,
                 send_email: bool = True,
                 local_db: str = None,
                 send_kafka: bool = True,
                 transfer: bool = True,
                 stats: bool = True,
                 verbose: bool = False,
                 log=None):
        self.topic_in = topic_in
        self.group_id = group_id
        self.maxmessage = int(maxmessage)
        self.local_db = local_db or 'ztf'
        self.send_email = send_email
        self.send_kafka = send_kafka
        self.transfer = transfer
        self.stats = stats
        self.verbose = verbose
        self.message_dict = {}

        self.consumer = None
        self.producer = None
        self.database_local = None
        self.database_remote = None

        self.log = log or lasairLogging.getLogger("filter")
        self.log.info('Topic_in=%s, group_id=%s, maxmessage=%d' % (self.topic_in, self.group_id, self.maxmessage))

        # catch SIGTERM so that we can finish processing cleanly
        self.prv_sigterm_handler = signal.signal(signal.SIGTERM, self._sigterm_handler)
        self.sigterm_raised = False

    def setup(self):
        """Set up connections to Kafka, database, etc. if not already done. It is safe to call this multiple
        times. We do this separately from __init__ mostly to facilitate testing."""

        # set up the Kafka consumer now
        if not self.consumer:
            self.consumer = self.make_kafka_consumer()

        # set up the Kafka producer now
        if not self.producer:
            self.producer = self.make_kafka_producer()

        # set up the link to the local database
        if not self.database_local or not self.database_local.is_connected():
            try:
                self.database_local = db_connect.local(self.local_db)
            except Exception as e:
                self.log.error('ERROR in Filter: cannot connect to local database' + str(e))
        # set up the link to the remote database
        if not self.database_remote or not self.database_remote.is_connected():
            try:
                self.database_remote = db_connect.remote()
            except Exception as e:
                self.log.error('ERROR in Filter: cannot connect to remote database' + str(e))

    def _sigterm_handler(self, signum, frame):
        """Handle SIGTERM by raising a flag that can be checked during the poll/process loop.
        """
        self.sigterm_raised = True
        self.log.debug("caught SIGTERM")
        # if we have already set a non-default handler then call that too
        if self.prv_sigterm_handler is not signal.SIG_DFL and not None:
            self.prv_sigterm_handler(signum, frame)

    def execute_local_query(self, query: str):
        """ execute_local_query: run a query and close it, and compalin to slack if failure.
        """
        try:
            cursor = self.database_local.cursor(buffered=True)
            cursor.execute(query)
            cursor.close()
            self.database_local.commit()
        except Exception as e:
            self.log.error('ERROR filter/execute_local_query: %s' % str(e))
            self.log.info(query)
            raise

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
            self.log.error('ERROR cannot make kafka consumer' + str(e))

    def make_kafka_producer(self):
        """ Make a kafka producer.
        """
        conf = {
            'bootstrap.servers': settings.PUBLIC_KAFKA_SERVER,
            'security.protocol': 'SASL_PLAINTEXT',
            'sasl.mechanisms': 'SCRAM-SHA-256',
            'sasl.username': settings.PUBLIC_KAFKA_USERNAME,
            'sasl.password': settings.PUBLIC_KAFKA_PASSWORD,
            'message.max.bytes': 10000000,
            'queue.buffering.max.messages': 10000000,
            'queue.buffering.max.kbytes': 2097152
        }

        self.log.info(str(conf))
        self.log.info('Topic in = %s' % self.topic_in)
        try:
            producer = confluent_kafka.Producer(conf)
            return producer
        except Exception as e:
            self.log.error('ERROR cannot make kafka producer' + str(e))

    def consume_messages(self, handler):
        """Consume a batch of messages from Kafka.
        """
        nmessage_in = nmessage_out = 0
        startt = time.time()
        errors = 0

        messageList = []
        while nmessage_in < self.maxmessage:
            if self.sigterm_raised:
                # clean shutdown - stop the consumer
                self.log.info("Caught SIGTERM, aborting.")
                break

            # Here we get the next message by kafka
            msg = self.consumer.poll(timeout=20)
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
            # Apply filter to each message
            message = json.loads(msg.value())

#            # don't know what to do with these
#            if 'diaObject' not in alert or not alert['diaObject']:
#                if self.verbose: print('No diaObject')
#                continue

            nmessage_in += 1
            messageList.append(message)

            # caching for fat kafka
            diaObjectId = message['diaObject']['diaObjectId']
            self.message_dict[diaObjectId] = message

            if nmessage_in % 1000 == 0:
                d = handler(messageList)
                messageList = []
                nmessage_out += d
                self.log.info('nmessage_in %d nmessage_out  %d time %.1f' % \
                              (nmessage_in, nmessage_out, time.time() - startt))
                sys.stdout.flush()
                # refresh the database every 1000 messages
                # make sure everything is committed
                self.database_local.commit()

        d = handler(messageList)
        nmessage_out += d
        self.log.info('finished %d in, %d out' % (nmessage_in, nmessage_out))

        if self.stats:
            ms = manage_status.manage_status(log=self.log)
            nid = date_nid.nid_now()
            ms.add({
                'today_filter': nmessage_in,
                'today_filter_out': nmessage_out,
            }, nid)

        return nmessage_out

    def transfer_to_main(self, retry=5, delay=60):
        """ Transfer the local database to the main database.
        retry: number of times to retry before giving up
        delay: delay between retries in seconds
        """
        cmd = 'sudo --non-interactive rm /data/mysql/*.txt'
        os.system(cmd)

        for count in range(1, retry+1):
            try:
                main_database = db_connect.remote(allow_infile=True)
                break
            except Exception as e:
                self.log.warning(f'filter/transfer_to_main failed to connect (attempt {count}/{retry}): ' + str(e))
                if count < retry:
                    time.sleep(delay)
                else:
                    self.log.error(f'filter/transfer_to_main failed to connect after {retry} attempts: ' + str(e))
                    return False

        for table_name, attrs in self.csv_attrs.items():
            for count in range(1, retry + 1):
                try:
                    transfer_csv(self.database_local, main_database, attrs, table_name, table_name, log=self.log)
                    self.log.info(f'{table_name} ingested to main db')
                    break
                except Exception as e:
                    self.log.warning(f'filter/transfer_to_main failed transfer (attempt {count}/{retry}): ' + str(e))
                    if count < retry:
                        time.sleep(delay)
                    else:
                        self.log.error(f'filter/transfer_to_main: cannot push {table_name} local to main database: ' + str(e))
                        return False

        self.consumer.commit()
        self.log.info('Kafka committed for this batch')
        return True

    def write_stats(self, timers: dict, nmessages: int):
        """ Write the statistics to lasair status and to prometheus.
        """
        if not self.stats:
            return

        ms = manage_status.manage_status(log=self.log)
        nid = date_nid.nid_now()
        d = Filter.batch_statistics(self.log)
        ms.set({
            'today_lsst': Filter.grafana_today(),
            'today_database': d['count'],
            'total_count': d['total_count'],
            'min_delay': d['since'],  # hours since most recent message
            'nid': nid},
            nid)
        for name, td in timers.items():
            td.add2ms(ms, nid)

        if nmessages > 0:
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
    def batch_statistics(log):
        """How many objects updated since last midnight.
        """
        mjdnow = (time.time() / 86400 + 40587)
        midnight = math.floor(mjdnow - 0.5) + 0.5

        msl_main = db_connect.readonly()
        cursor = msl_main.cursor(buffered=True, dictionary=True)

        # objects modified since last midnight
        query = 'SELECT count(*) AS count FROM objects WHERE lastDiaSourceMjdTai > %.1f' % midnight
        try:
            cursor.execute(query)
            for row in cursor:
                count = row['count']
                break
        except Exception as e:
            log.warning("batch_statistics today: %s %s" % (str(e), query))
            count = -1

        # total number of objects
        query = 'SELECT count(*) AS total_count, mjdnow()-max(lastDiaSourceMjdTai) AS since FROM objects'

        try:
            cursor.execute(query)
            for row in cursor:
                total_count = row['total_count']
                try:
                    since = 24*float(row['since'])
                except:
                    since = 1000000000.0
                break
        except Exception as e:
            log.warning("batch_statistics total: %s %s" % (str(e), query))
            total_count = -1
            since = -1

        # statistics for most recent batch
        min_delay = -1
        avg_delay = -1
        max_delay = -1
        msl_local = db_connect.local()
        cursor = msl_local.cursor(buffered=True, dictionary=True)
        query = 'SELECT '
        query += 'mjdnow()-max(lastDiaSourceMjdTai) AS min_delay, '
        query += 'mjdnow()-avg(lastDiaSourceMjdTai) AS avg_delay, '
        query += 'mjdnow()-min(lastDiaSourceMjdTai) AS max_delay '
        query += 'FROM objects'
        try:
            cursor.execute(query)
            for row in cursor:
                print(row)
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
        g = datetime.datetime.now(datetime.UTC)
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

if __name__ == "__main__":
    #lasairLogging.basicConfig(stream=sys.stdout)
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()
    args = docopt(__doc__)

    topic_in = args.get('--topic_in') or 'lsst_sherlock'
    group_id = args.get('--group_id') or settings.KAFKA_GROUPID
    maxmessage = int(args.get('--maxmessage') or settings.KAFKA_MAXALERTS)
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
    verbose = args.get('--verbose') in ['True', 'true', 'Yes', 'yes']

############### choose which type of message, are they alerts or annotations ########
    from alerts import alertcore
    fltr = alertf = alertcore.AlertFilter(
            topic_in=topic_in, group_id=group_id, maxmessage=maxmessage, 
            local_db=local_db, send_email=send_email, send_kafka=send_kafka, 
            transfer=transfer, stats=stats, verbose=verbose)
    alertf.setup()
########################################################################

    n_batch = 0
    total_messages = 0
    while not fltr.sigterm_raised:

        # the subclass is handed a list of messages (alerts or annotations)
        alertf.setup_batch()

        # calls handle_message_list for subclass
        iml = alertf.ingest_message_list
        n_messages = fltr.consume_messages(iml)

        if n_messages > 0:
            alertf.post_ingest(n_messages)

        # keep a cache
        fltr.message_dict.clear()

        n_batch += 1
        total_messages += n_messages 
        if n_batch == maxbatch:
            log.info(f"Exiting after {n_batch} batches")
            sys.exit(0)
        if maxtotal and total_messages >= maxtotal:
            log.info(f"Exiting after {total_messages} messages")
            sys.exit(0)
        if n_messages == 0:  # process got no messages, so sleep a few minutes
            log.info('Waiting for more messages ....')
            time.sleep(wait_time)
