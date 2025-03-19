import json, sys
import object_features
import read_avsc

lasair_schema = object_features.schema

if len(sys.argv) < 2:
    print('Usage: join_object_schema.py <schema_version> ... example 704')
    sys.exit()
schema_version = sys.argv[1]
diaObject_schema = read_avsc.read_from_github(schema_version, 'diaObject')

fields = []
names = []
for f in lasair_schema['fields']:
    if 'section' in f: 
        fields.append(f)
    if 'name' in f:
        fields.append(f)
        names.append(f['name'])

ext_fields = []
for f in diaObject_schema['fields']:
    if not f['name'] in names:
        ext_fields.append(f)

print('%d core and %d extended attributes' % (len(fields), len(ext_fields)))

object_schema = {
    "name": "objects",
    "fields": fields,
    "ext_fields": ext_fields,
    "indexes": [
        "PRIMARY KEY (diaObjectId)",
        "KEY htmid16idx (htm16)",
        "KEY idxMaxTai (lastDiaSourceMJD)"
      ]
    }

filename = '%s/objects.py' % schema_version
out = open(filename, 'w')
out.write('schema = ' + json.dumps(object_schema, indent=2))
out.close()
print(filename, 'written')
