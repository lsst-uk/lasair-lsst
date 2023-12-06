import os, sys, json, io
import fastavro

if __name__ == '__main__':
    datadir = 'data/' + sys.argv[1]

    schemafile = '../../common/schema/dp02.avsc'
    schema = json.loads(open(schemafile).read())
#    parsed_schema = fastavro.parse_schema(schema)

    for file in os.listdir(datadir):
        tok = file.split('.')
        if len(tok) < 2 or tok[1] != 'avro':
            continue
        fileroot = tok[0]
        stream = open(datadir +'/'+ fileroot + '.avro', 'rb')
        alert = fastavro.schemaless_reader(stream, schema)

        jsonfile = open(datadir +'/'+ fileroot + '_new.json', 'w')
        s = json.dumps(alert, indent=2)
        print(file, len(s))
        jsonfile.write(s)
        jsonfile.close()
