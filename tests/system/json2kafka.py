import os, sys, json, io, gzip
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    if len(sys.argv) >= 4:
        broker = sys.argv[1]
        datafile = sys.argv[2]
        topic = sys.argv[3]
    else:
        print('Usage: json_to_kafka.py <broker> <file> <topic>')
        sys.exit()

    schemafile = '../../common/schema/dp02.avsc'
    schema = json.loads(open(schemafile).read())
    parsed_schema = fastavro.parse_schema(schema)

    conf = {
        'bootstrap.servers': broker,
        'client.id': 'client-1',
    }
    p = Producer(conf)

    objList = None
    fin = open(datafile, 'r')
    json_str = fin.read()
    fin.close()

    obj = json.loads(json_str)          

    # there will never be an alert with no detections
    if obj['DiaObject']['nDiaSources'] < 1:
        sys.exit(0)

    diaObjectId = str(obj['DiaObject']['diaObjectId'])
    #s = json.dumps(obj, indent=2)
    mockfile = io.BytesIO()
    fastavro.schemaless_writer(mockfile, parsed_schema, obj)
    p.produce(topic, mockfile.getvalue())
    p.flush()

