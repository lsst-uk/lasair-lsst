import os, sys, json
import fastavro

if __name__ == '__main__':
    datadir = 'data/' + sys.argv[1]

    schemafile = '../../common/schema/dp02.avsc'
    schema = json.loads(open(schemafile).read())
    parsed_schema = fastavro.parse_schema(schema)

    for file in os.listdir(datadir):
        tok = file.split('.')
        if len(tok) < 2 or tok[1] != 'json':
            continue
        fileroot = tok[0]
        s = open(datadir +'/'+ fileroot + '.json').read()
        print(file, len(s))
        obj = json.loads(s)
        avrofile = open(datadir +'/'+ fileroot + '.avro', 'wb')
        fastavro.schemaless_writer(avrofile, parsed_schema, obj)
