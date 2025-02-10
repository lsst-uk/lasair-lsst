import os, sys, json, io, gzip
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        datadir    = sys.argv[1]
        topic      = sys.argv[2]
    else:
        print('Usage: json_to_kafka.py <dataset> <topic>')
        sys.exit()

    conf = {
        'bootstrap.servers': 'lasair-lsst-dev-kafka-0:9092',
        'client.id': 'client-1',
    }
    p = Producer(conf)

    n = 0
    objList = None
    for file in os.listdir(datadir):
        if not file.endswith('json'): continue
        
        fin = open(datadir +'/'+ file, 'r')
        json_str = fin.read()
        fin.close()

        p.produce(topic, json_str)
        n +=1
        if n%100 == 0: 
            print(n)
            p.flush()
            p = Producer(conf)
    p.flush()
    print('%d alerts pushed to topic %s' % (n, topic))
