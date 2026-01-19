"""
2_join_object_schema.py
The MySQL object schema is special, it involves the Lasair features, the core 
attributes from the Rubin schema, and the extended attributes.

The file object_features.py serves a prototype of the lasair and core attributes,
and the extended attributes are pulled from the diaObject schema.
"""

import json, sys
import object_features
import read_avsc

lasair_schema = object_features.schema

if len(sys.argv) < 2:
    print('Usage: join_object_schema.py <schema_version> ... example 7_4')
    sys.exit()
schema_version = sys.argv[1]
if len(sys.argv) >= 3:
    branch = sys.argv[2]
else:
    branch = 'main'

# The Rubin diaObject schema
diaObject_schema = read_avsc.read_from_github(schema_version, 'diaObject', branch)

# this will be the finished schema
fields = []

# list of all the attribute names in the object_features schema
names = []

for f in lasair_schema['fields']:
    if 'section' in f: 
        fields.append(f)           # copy in section headings
    if 'name' in f:
        fields.append(f)           # copy in the field
        names.append(f['name'])    # add to list of names

# Everything not already in the object schema goes into extended fields
ext_fields = []
for f in diaObject_schema['fields']:
    if not f['name'] in names:
        ext_fields.append(f)

print('%d core and %d extended attributes' % (len(fields), len(ext_fields)))

# Now just write it out
object_schema = {
    "name": "objects",
    "fields": fields,
    "ext_fields": ext_fields,
    "indexes": [
        "PRIMARY KEY (diaObjectId)",
        "KEY htmid16idx (htm16)",
        "KEY idxMaxTai (lastDiaSourceMjdTai)"
      ]
    }

filename = '%s/objects.py' % schema_version
out = open(filename, 'w')
out.write('schema = ' + json.dumps(object_schema, indent=2))
out.close()
print(filename, 'written')
