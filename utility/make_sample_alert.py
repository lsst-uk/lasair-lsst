"""
make_sample_alert.py
Use "simple alerts" combined with selected schema to make LSST alerts,
with most of the attributes set to zero or some other default.
Example input:
{
    "objectId": "Active_galactic_nucleus_AGN_54063785",
    "observation_reason": "plasticc",
    "target_name": "Active_galactic_nucleus_AGN",
    "candidates": [
        {
            "midpointMjdTai": 59584.073,
            "psfFlux": 777.190674,
            "psfFluxErr": 41.012691,
            "band": "u",
            "ra": 301.48454525887274,
            "dec": 9.5206549640737
        },
etc etc
"""
import os, sys, random
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
    if len(sys.argv) > 3:
        schema_version = sys.argv[1]
        indir          = sys.argv[2]
        outdir         = sys.argv[3]
    else:
        print("Usage: make_sample_alert.py schema_version indir outdir")
        print("schema_verrsion can be for example 7_4_A")
        print("sample alert goes to outfile, can use infile if provided")
        sys.exit()

    component = 'diaSources'
    schema_package = importlib.import_module('%s.%s' % (schema_version, component))
    schema = schema_package.schema
    ds_default = makeDefault(component)

    component = 'diaObjects'
    schema_package = importlib.import_module('%s.%s' % (schema_version, component))
    schema = schema_package.schema
    dobj = makeDefault(component)

    attrs = ['midpointMjdTai', 'ra', 'dec', 'band', 'psfFlux', 'psfFluxErr']
    for file in os.listdir(indir):
        inalert = json.loads(open(indir +'/'+ file).read())
        numerical_objectId = abs(hash(inalert['objectId']))
        print('converting %s --> %d' % (inalert['objectId'], numerical_objectId))
        cands = inalert['candidates']

        dslist = []
        ralist = []
        declist = []
        for cand in cands:
            ds = ds_default.copy()
            ralist.append(cand['ra'])
            declist.append(cand['dec'])
            for attr in attrs:
                ds[attr] = cand[attr]
            ds['diaObjectId'] = numerical_objectId
            ds['diaSourceId'] = random.randint(1, 100000000000)
            dslist.append(ds)
        dobj['diaObjectId'] = numerical_objectId
        dobj['ra'] = sum(ralist)/len(ralist)
        dobj['dec'] = sum(declist)/len(declist)
        alert = {
            'diaObjectId': numerical_objectId,
#            'observation_reason': inalert['observation_reason'][:16],
#            'target_name': inalert['target_name'][:16],
            'diaObject': dobj,
            'diaSource': dslist[-1],
            'prvDiaSources': dslist[:-1],
        }
    
        f = open(outdir +'/'+ file, 'w')
        f.write(json.dumps(alert, indent=2))
        f.close()
        print('Wrote ', file)
