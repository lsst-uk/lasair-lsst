import sys
sys.path.append('../../common')
from src import db_connect
import settings

class Filter():
    def __init__(self, args):
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
        self.log.info('Topic_in=%s, group_id=%s, maxalert=%d' % (topic_in, group_id, maxalert))
    
        self.timers = {}
        for name in ['ffeatures', 'fwatchlist', 'fwatchmap', 'ffilters', 'ftransfer', 'ftotal']:
            self.timers[name] = manage_status.timer(name)

        try:
            self.msl = db_connect.local()
        except:
            self.log.error('ERROR in filter/refresh: cannot clear local database')
            sys.stdout.flush()

    def truncate():
        cursor = self.msl.cursor(buffered=True, dictionary=True)
        cursor.execute('TRUNCATE TABLE objects')
        cursor.execute('TRUNCATE TABLE sherlock_classifications')
        cursor.execute('TRUNCATE TABLE watchlist_hits')
        cursor.execute('TRUNCATE TABLE area_hits')

    def consumer():
        conf = {
            'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
            'enable.auto.commit': False,   # require explicit commit!
            'self.group.id':           group_id,
            'max.poll.interval.ms': 20*60*1000,  # 20 minute timeout in case queries take time
            'default.topic.config': {
                'auto.offset.reset': 'earliest'
            }
        }
        print(conf, topic_in)
        self.log.info(str(conf))
        self.log.info('Topic in = %s' % topic_in)
        try:
            consumer = confluent_kafka.Consumer(conf)
            consumer.subscribe([topic_in])
            return consumer
        except Exception as e:
            log.error('ERROR cannot connect to kafka', e)
            return None
