"""
1_fetch_avsc.py
for a given schema version, for example 7_4_a, pull the major and minor revision
numbers (7 and 4) and use them to 
- read the avsc files from github
    - change dec to decl
    - replace "type":["null","float"] with "type":"float"
- add in the index for the CQL table
- write as a .py file in the directory for that schema version
"""

import json, sys
import read_avsc

if len(sys.argv) < 2:
    print('Usage: fetch_avsc.py <schema_version> ... example 704')
    sys.exit()
schema_version = sys.argv[1]
tok = schema_version.split('_')
major_sv = tok[0]
minor_sv = tok[1]

baseUrl = 'https://raw.githubusercontent.com/lsst/alert_packet/refs/heads/main/python/lsst/alert/packet/schema/%s/%s/lsst.v%s_%s.'
baseUrl = baseUrl % (major_sv, minor_sv, major_sv, minor_sv)

cql_indexes = {
    "diaForcedSource"     :"PRIMARY KEY (\"diaObjectId\",\"midpointMjdTai\")",
    "diaNondetectionLimit":"PRIMARY KEY (\"midpointMjdTai\")",
    "diaObject"           :"PRIMARY KEY (\"diaObjectId\")",
    "diaSource"           :"PRIMARY KEY (\"diaObjectId\", \"midpointMjdTai\", \"diaSourceId\")",
    "ssObject"            :"PRIMARY KEY (\"ssObjectId\")"
}

for component,index in cql_indexes.items():
    print(component)
    d = read_avsc.read_from_github(schema_version, component)
    s = "schema = {\n  'indexes':['%s']," % index
    s += json.dumps(d, indent=2)[1:]
    f = open('%s/%ss.py' % (schema_version, component), 'w')
    f.write(s)
    f.close()
