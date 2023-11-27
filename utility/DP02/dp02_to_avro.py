import os, sys, json
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    datadir = 'data/' + sys.argv[1]

    schemafile = 'schema/dp02.avsc'
    schema = json.loads(open(schemafile).read())
    parsed_schema = fastavro.parse_schema(schema)

    conf = {
        'bootstrap.servers': 'lasair-lsst-dev-kafka:9092',
        'client.id': 'client-1',
    }
    p = Producer(conf)
    topic = 'DP02'
    for file in os.listdir(datadir):
        tok = file.split('.')
        if len(tok) < 2 or tok[1] != 'json':
            continue
        fileroot = tok[0]
        s = open(datadir +'/'+ fileroot + '.json').read()
        print(file, len(s))
        obj = json.loads(s)
        avrofile = open(datadir +'/'+ fileroot + '.avro', 'wb')
        fastavro.writer(avrofile, parsed_schema, [obj])
