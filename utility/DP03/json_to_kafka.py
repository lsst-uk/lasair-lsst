import os, sys, json, io, gzip
import fastavro
from confluent_kafka import Producer, KafkaError

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        datadir = sys.argv[1]
        topic   = sys.argv[2]
    else:
        print('Usage: json_to_kafka.py <dataset> <topic>')
        sys.exit()

#    schemafile = 'dp03.avsc'
#    schema = json.loads(open(schemafile).read())
#    parsed_schema = fastavro.parse_schema(schema)

    conf = {
        'bootstrap.servers': 'lasair-lsst-kafka:9092',
        'client.id': 'client-1',
    }
    p = Producer(conf)

    n = 0
    objList = None
    print(datadir)
    for file in os.listdir(datadir):
        if not file.endswith('gz'): continue
        print(file)
        
        del objList
        fin = gzip.open(datadir +'/'+ file, 'r')
        json_bytes = fin.read()
        fin.close()

        json_str = json_bytes.decode('utf-8')
        del json_bytes
        objList = json.loads(json_str)          
        del json_str

        for obj in objList:
#            print(len(obj['DiaSourceList']), len(obj['SSSourceList']))

            # there will never be an alert with no detections
            if len(obj['DiaSourceList']) < 1: continue

            ssObjectId = str(obj['SSObjectId'])
            
            alert_obj = {
                'SSObjectId' : obj['SSObjectId'],
                'SSObject'   : obj['SSObject'],
                'MPCORB'     : obj['MPCORB'],
                'DiaSource'  : obj['DiaSourceList'][0],
                'SSSource'   : obj['SSSourceList'][0],
            }

            s = json.dumps(alert_obj, indent=2)
#            mockfile = io.BytesIO()
#            fastavro.schemaless_writer(mockfile, parsed_schema, obj)
#            p.produce(topic, mockfile.getvalue())
            p.produce(topic, s.encode('utf-8'))
            n +=1
            if n%100 == 0: 
                print(n)
                p.flush()
                p = Producer(conf)
    p.flush()
    print('%d alerts pushed to topic %s' % (n, topic))
