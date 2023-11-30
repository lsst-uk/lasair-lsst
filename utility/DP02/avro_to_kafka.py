import os, sys, json
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    datadir = 'data/' + sys.argv[1]

    conf = {
        'bootstrap.servers': 'lasair-lsst-dev-kafka:9092',
        'client.id': 'client-1',
    }
    p = Producer(conf)
    topic = 'DP02new'
    for file in os.listdir(datadir):
        tok = file.split('.')
        if len(tok) < 2 or tok[1] != 'avro':
            continue
        fileroot = tok[0]
        avrofile = open(datadir +'/'+ fileroot + '.avro', 'rb')
        p.produce(topic, avrofile.read())
        p.flush()
