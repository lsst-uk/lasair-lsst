import os, sys, json, io, gzip
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    if len(sys.argv) >= 4:
        datadir    = sys.argv[1]
        schemafile = sys.argv[2]
        topic      = sys.argv[2]
    else:
        print('Usage: json_to_kafka.py <dataset> <schemafile> <topic>')
        sys.exit()

    schema = json.loads(open(schemafile).read())
    parsed_schema = fastavro.parse_schema(schema)

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

        obj = json.loads(json_str)          

        mockfile = io.BytesIO()
        fastavro.schemaless_writer(mockfile, parsed_schema, obj)
        p.produce(topic, mockfile.getvalue())
        n +=1
        if n%100 == 0: 
            print(n)
            p.flush()
            p = Producer(conf)
    p.flush()
    print('%d alerts pushed to topic %s' % (n, topic))
