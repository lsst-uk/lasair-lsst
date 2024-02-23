import sys, json, argparse
from confluent_kafka import Consumer, KafkaError
import json

parser = argparse.ArgumentParser(description=__doc__)
# must provide broker name, examples
#kafka = 'public.alerts.ztf.uw.edu:9092'
#kafka = 'kafka.lsst.ac.uk:9092'
#kafka = 'lasair-lsst-dev-kafka:9092'
parser.add_argument('--broker', type=str, help='address:port of Kafka broker(s)')

# if no topic, prints available topics
parser.add_argument('--topic',  type=str, default=None, help='topic to be comsumed')

# if not group_id, uses Lasair pipeline group_id
parser.add_argument('--group_id',  type=str, default='LASAIR1', help='group id to use for Kafka')

# print one and exit, or count all to end of group_id
parser.add_argument('--print_one', action="store_true", default=None, help='Prints one and exits')

q = vars(parser.parse_args())
if not q.get('broker'):
    print('Must set kafka broker with --broker option')
    sys.exit()
print(q)

conf = {
    'bootstrap.servers':   q.get('broker'),
    'group.id':            q.get('group_id'),
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}
streamReader = Consumer(conf)

if not q.get('topic'):
    # the topics that this server has
    t = list(streamReader.list_topics().topics.keys())
    print('Topics are ', t)
else:
    nalert = 0
    # content of given topic
    topic = q.get('topic')
    streamReader.subscribe([topic])
    while 1:
        msg = streamReader.poll(timeout=5)
        if msg == None: break
        if q['print_one']:
            print(msg.value())
            sys.exit()
        nalert += 1
        if nalert%1000 == 0: print(nalert)
    print('final', nalert)

streamReader.close()

