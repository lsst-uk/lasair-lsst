"""
make_sample_alert.py
use file info or just zeros to make a sample alert
"""
import sys
sys.path.append('../common/schema')
import prims
import json
import importlib

def makeDefault(name):
    tablename = schema['name']
    obj = {}
    # go through all the fields
    for f in schema['fields']:
        obj[f['name']] = prims.default(f['type'])
    return obj

if __name__ == '__main__':
    attrs = ['midpointMjdTai', 'ra', 'dec', 'band', 'psfFlux', 'psfFluxErr']
    infile = None
    if len(sys.argv) > 1:
        schema_version = sys.argv[1]
    else:
        print("Usage: make_sample_alert.py schema_version outfile [infile]")
        print("schema_verrsion can be for example 7_4_A")
        print("sample alert goes to outfile, can use infile if provided")
        sys.exit()
    if len(sys.argv) > 2:
        outfile           = sys.argv[2]
    if len(sys.argv) > 3:
        infile           = sys.argv[3]
        # infile should have objectId and list of candidates, each with
        # radecMjdTai, ra dec, band, psfFlux, psfFluxErr

    component = 'diaSources'
    schema_package = importlib.import_module('%s.%s' % (schema_version, component))
    schema = schema_package.schema
    ds = makeDefault(component)

    component = 'diaObjects'
    schema_package = importlib.import_module('%s.%s' % (schema_version, component))
    schema = schema_package.schema
    dobj = makeDefault(component)

    if infile:
        inalert = json.loads(open(infile).read())
        numerical_objectId = abs(hash(inalert['objectId']))
        print('converting %s --> %d' % (inalert['objectId'], numerical_objectId))
        cands = inalert['candidates']

    dslist = []
    for cand in cands:
        ds['diaObjectId'] = numerical_objectId
        for attr in attrs:
            ds[attr] = cand[attr]
        dslist.append(ds)
    alert = {
        'diaObjectId': numerical_objectId,
        'observation_reason': inalert['observation_reason'],
        'target_name': inalert['target_name'],
        'diaObject': dobj,
        'diaSource': dslist[-1],
        'prvdiaSources': dslist[:-1],
    }
    f = open(outfile, 'w')
    f.write(json.dumps(alert, indent=2))
    f.close()
    print('Wrote ', outfile)
