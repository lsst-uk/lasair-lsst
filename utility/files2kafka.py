""" Ingest avro files from a directory and convert to a kafka topic
    up to a maximum maxalert
"""
import os, sys
sys.path.append('../common')
import settings
from confluent_kafka import Producer, KafkaError

if len(sys.argv) < 3:
    print('Usage: files2kafka.py directory topic <maxalert>')
    sys.exit()

directory = sys.argv[1]
topic     = sys.argv[2]

maxalert = -1
if len(sys.argv) > 3:
    maxalert = int(sys.argv[3])

conf = {
    'bootstrap.servers': settings.KAFKA_SERVER,
    'client.id': 'client-1',
}

p = Producer(conf)

filenames = sorted(os.listdir(directory))

nalert = 0
for filename in filenames:
    message = open(directory +'/'+ filename, 'rb').read()
    p.produce(topic, message)
    nalert += 1
    if maxalert > 0 and nalert >= maxalert:
        break
    if nalert%1000 == 0:
        print(nalert)
        p.flush()
p.flush()
print('%d alerts ingested from directory %s to topic %s' % (nalert, directory, topic))
