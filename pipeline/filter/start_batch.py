"""
Filter code for Lasair.
    fetch a batch of alerts from kafka
    run the watchlist code and insert the hits
    run the active user queries and produce kafka
    build a CSV file of three tables with the batch:
      objects, sherlock_classifications, watchlist_hits, area_hits
    send data to main db with mysql --host

Usage:
    filter.py [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN]

Options:
    --maxalert=MAX     Number of alerts to process, default is from settings.
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, default is from settings
"""

import sys
import confluent_kafka
from docopt import docopt
import signal

sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import date_nid, db_connect, manage_status, lasairLogging

sys.path.append('../../common')
from src import db_connect

class Batch():
    def __init__(self):
        args = docopt(__doc__)

        if args['--topic_in']:
            self.topic_in = args['--topic_in']
        else:
            self.topic_in  = 'ztf_sherlock'
    
        if args['--group_id']:
            self.group_id = args['--group_id']
        else:
            self.group_id = settings.KAFKA_GROUPID
    
        if args['--maxalert']:
            self.maxalert = int(args['--maxalert'])
        else:
            self.maxalert = settings.KAFKA_MAXALERTS
    
        self.log = lasairLogging.getLogger("filter")
        self.log.info('Topic_in=%s, group_id=%s, maxalert=%d' % (self.topic_in, self.group_id, self.maxalert))
    
        self.timers = {}
        for name in ['ffeatures', 'fwatchlist', 'fwatchmap', 'ffilters', 'ftransfer', 'ftotal']:
            self.timers[name] = manage_status.timer(name)

        try:
            self.database = db_connect.local()
        except Exception as e:
            self.log.error('ERROR in run_batch: cannot connect to local database' + str(e))
        return

    def truncate_local_database(self):
        cursor = self.database.cursor(buffered=True, dictionary=True)
        cursor.execute('TRUNCATE TABLE objects')
        cursor.execute('TRUNCATE TABLE sherlock_classifications')
        cursor.execute('TRUNCATE TABLE watchlist_hits')
        cursor.execute('TRUNCATE TABLE area_hits')

    def make_kafka_consumer(self):
        conf = {
            'bootstrap.servers'   : '%s' % settings.KAFKA_SERVER,
            'enable.auto.commit'  : False,   # require explicit commit!
            'group.id'            : self.group_id,
            'max.poll.interval.ms': 20*60*1000,  # 20 minute timeout in case queries take time
            'default.topic.config': {
                'auto.offset.reset': 'earliest'
            }
        }
        self.log.info(str(conf))
        self.log.info('Topic in = %s' % self.topic_in)
        try:
            self.consumer = confluent_kafka.Consumer(conf)
            self.consumer.subscribe([self.topic_in])
        except Exception as e:
            self.log.error('ERROR cannot connect to kafka', e)
