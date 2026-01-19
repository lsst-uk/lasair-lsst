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
    print('Usage: fetch_avsc.py <schema_version> [branch] ... example 7_4')
    sys.exit()
schema_version = sys.argv[1]
tok = schema_version.split('_')
major_sv = tok[0]
minor_sv = tok[1]
if len(sys.argv) >= 3:
    branch = sys.argv[2]
else:
    branch = 'main'

cql_indexes = {
    "diaForcedSource"     :"PRIMARY KEY (\"diaObjectId\",\"midpointMjdTai\")",
    "diaNondetectionLimit":"PRIMARY KEY (\"midpointMjdTai\")",
    "diaObject"           :"PRIMARY KEY (\"diaObjectId\")",
    "diaSource"           :"PRIMARY KEY (\"diaObjectId\", \"midpointMjdTai\", \"diaSourceId\")",
    "ssObject"            :"PRIMARY KEY (\"ssObjectId\")",
    "ssSource"            :"PRIMARY KEY (\"ssObjectId\", \"diaSourceId\")",
    "mpc_orbits"          :"PRIMARY KEY (\"designation\")",
}

for component,index in cql_indexes.items():
    print(component)

    # change mpc_orbit to singular for lasair
    lasair_name = component
    if component == 'mpc_orbits':
        lasair_name = 'mpc_orbit'

    try:
        d = read_avsc.read_from_github(schema_version, component, branch)
    except Exception as e:
        print('Could not handle component', component)
    s = "schema = {\n  'indexes':['%s']," % index
    s += json.dumps(d, indent=2)[1:]
    f = open('%s/%ss.py' % (schema_version, lasair_name), 'w')
    f.write(s)
    f.close()
