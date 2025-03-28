import sys, json
sys.path.append('../../../../../common/schema/7_4')
import diaObjects, diaSources

default = {
    'boolean':'true',
    'float'  :0.0,
    'double' :0.0,
    'int'    : 0,
    'long'   : 12345678,
    'string' : 'u',
}

if len(sys.argv) > 1:
    infile = sys.argv[1]
else:
    print('Usage: make_sample_alert <input_file>')
    sys.exit()

detections = json.loads(open(infile).read())

s_obj = diaObjects.schema
s_src = diaSources.schema

dobj = {}
for f in s_obj['fields']:
    dobj[f['name']] = default[f['type']]

dsl = []
for detection in detections:
    ds  = {}
    for f in s_src['fields']:
        ds[f['name']] = default[f['type']]
    ds['midpointMjdTai'] = detection['mjd']
    ds['psfFlux']        = detection['flux']
    ds['psfFluxErr']     = detection['flux_err']
    ds['band']           = detection['band']
    dsl.append(ds)

d = {}
d['diaObject'] = dobj
d['diaSourcesList'] = dsl
d['diaForcedSourcesList'] = []
d['diaNondetectionLimitsList'] = []
d['ssObject'] = None

print(json.dumps(d, indent=2))
