import os, json
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    datadir = '../data/data_0005_10'

    schemafile = '../schema/dp02.avsc'
    schema = json.loads(open(schemafile).read())
    parsed_schema = fastavro.parse_schema(schema)

    conf = {
        'bootstrap.servers': 'lasair-lsst-dev-kafka:9092',
        'client.id': 'client-1',
    }
    p = Producer(conf)
    topic = 'DP02'
    for file in os.listdir(datadir):
        s = open(datadir +'/'+ file).read()
        print(file, len(s))
        obj = json.loads(s)
        tmp = open('tmp.avro', 'wb')
        fastavro.writer(tmp, parsed_schema, [obj])
        tmp = open('tmp.avro', 'rb')
        alert = tmp.read()
        tmp.close()
        os.remove('tmp.avro')
        p.produce(topic, alert)
        p.flush()
