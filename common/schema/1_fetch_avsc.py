import json, sys
import read_avsc

if len(sys.argv) < 2:
    print('Usage: fetch_from_github.py <schema_version> ... example 704')
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
