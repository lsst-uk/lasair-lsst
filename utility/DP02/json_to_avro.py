import os, sys, json, gzip
import fastavro

if __name__ == '__main__':
    datadir = sys.argv[1]

    schemafile = '../../common/schema/dp02.avsc'
    schema = json.loads(open(schemafile).read())
    parsed_schema = fastavro.parse_schema(schema)

    n = 0
    objList = None
    for file in os.listdir(datadir):
        if not file.endswith('gz'): continue
        print('opening ', file)
        
        del objList
        fin = gzip.open(datadir +'/'+ file, 'r')
        json_bytes = fin.read()
        fin.close()

        json_str = json_bytes.decode('utf-8')
        del json_bytes
        objList = json.loads(json_str)          
        del json_str

        print('found %d objects' % len(objList))

        for obj in objList:
            diaObjectId = str(obj['DiaObject']['diaObjectId'])
            s = json.dumps(obj, indent=2)
            avrofile = open(datadir +'/'+ diaObjectId + '.avro', 'wb')
            fastavro.schemaless_writer(avrofile, parsed_schema, obj)
            avrofile.close()
            n += 1
            if n % 100 == 0:
                print(n)
