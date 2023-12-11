import os, sys, json, gzip
import fastavro

if __name__ == '__main__':
    datadir = 'data/' + sys.argv[1]

    schemafile = '../../common/schema/dp02.avsc'
    schema = json.loads(open(schemafile).read())
    parsed_schema = fastavro.parse_schema(schema)

    for file in os.listdir(datadir):
        if not file.endswith('gz'): continue
        
        with gzip.open(datadir +'/'+ file, 'r') as fin:
            json_bytes = fin.read()

        json_str = json_bytes.decode('utf-8')
        objList = json.loads(json_str)          

        for obj in objList:
            diaObjectId = str(obj['DiaObject']['diaObjectId'])
            s = json.dumps(obj, indent=2)
            avrofile = open(datadir +'/'+ diaObjectId + '.avro', 'wb')
            fastavro.schemaless_writer(avrofile, parsed_schema, obj)
