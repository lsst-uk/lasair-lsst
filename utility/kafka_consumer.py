import sys, json, argparse
from confluent_kafka import Consumer, KafkaError
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import json

def print_msg(message):
    """ prints the readable stuff, without the cutouts. Purely for debugging
    """
    message_text = {k: message[k] for k in message
        if k not in ['cutoutDifference', 'cutoutTemplate', 'cutoutScience']}
    print(json.dumps(message_text, indent=2))

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

# utilise schema registry
parser.add_argument('--schema_reg', type=str, default=None, help='Fetches with schema registry')
# example https://usdf-alert-schemas-dev.slac.stanford.edu

q = vars(parser.parse_args())
if not q.get('broker'):
    print('Must set kafka broker with --broker option')
    sys.exit()
print(q)
sr = q.get('schema_reg')
if sr:
    print('using schema_reg', sr)

conf = {
    'bootstrap.servers':   q.get('broker'),
    'group.id':            q.get('group_id'),
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}
if sr:
    sr_client = SchemaRegistryClient({"url": sr})
    deserializer = AvroDeserializer(sr_client)
    conf['value.deserializer'] = deserializer
    streamReader = DeserializingConsumer(conf)
else:
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
        if msg == None: 
            break
        if msg.error():
            print('ERROR in ingest/poll: ' +  str(msg.error()))
            break
        if q['print_one']:
#            print(msg.value())
            print_msg(msg.value())
            #sys.exit()
            break
        nalert += 1
        if nalert%1000 == 0: print(nalert)
    print('final', nalert)

streamReader.close()

