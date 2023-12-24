import os, sys, json
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        datadir = sys.argv[1]
        topic   = sys.argv[2]
    else:
        print('Usage: avro_to_kafka.py <dataset> <topic>')
        sys.exit()

    conf = {
        'bootstrap.servers': 'lasair-lsst-dev-kafka:9092',
        'client.id': 'client-1',
    }
    p = Producer(conf)
    n = 0
    for file in os.listdir(datadir):
        tok = file.split('.')
        if len(tok) < 2 or tok[1] != 'avro':
            continue
        fileroot = tok[0]
        avrofile = open(datadir +'/'+ fileroot + '.avro', 'rb')
        p.produce(topic, avrofile.read())
        p.flush()
        n +=1
    print('%d alerts pushed to topic %s' % (n, topic))
