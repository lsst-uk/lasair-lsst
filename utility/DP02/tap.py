import sys, os, requests, time, settings, json
import pyvo as pyvo
import numpy as np
from astropy.io import ascii

url = 'https://data.lsst.cloud/api/tap'

session = requests.Session()
session.headers["Authorization"] = "Bearer " + settings.RSP_TOKEN
auth = pyvo.auth.authsession.AuthSession()
auth.credentials.set("lsst-token", session)
auth.add_security_method_for_url(url, "lsst-token")
auth.add_security_method_for_url(url + "/sync", "lsst-token")
auth.add_security_method_for_url(url + "/async", "lsst-token")
auth.add_security_method_for_url(url + "/tables", "lsst-token")

service = pyvo.dal.TAPService(url, auth)

def getDiaObject(howMany, howManySources):
    query = """
    SELECT TOP %d *
    FROM dp02_dc2_catalogs.DiaObject 
    WHERE nDiaSources > %d """
    query = query % (howMany, howManySources)

    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return list(DiaSrcs)

def getDiaSource(diaObjectId):
    query = """
    SELECT *
    FROM dp02_dc2_catalogs.DiaSource
    WHERE diaObjectId = """ + str(diaObjectId)

    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return list(DiaSrcs)

def getForcedSourceOnDiaObject(diaObjectId):
    query = """
    SELECT *
    FROM dp02_dc2_catalogs.ForcedSourceOnDiaObject
    WHERE diaObjectId = """ + str(diaObjectId)

    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return list(DiaSrcs)

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

if __name__ == '__main__':
    if len(sys.argv) > 2:
        howMany        = int(sys.argv[1])
        howManySources = int(sys.argv[2])
    else:
        howMany = 5
        howManySources = 10

    print('Fetching %d objects with more than %d sources' % (howMany, howManySources))
    dir = 'data/data_%04d_%d' % (howMany, howManySources)
    os.system('mkdir -p %s' % dir)

    diaObjectList = getDiaObject(howMany, howManySources)

    t00 = t0 = time.time()
    n = 0
    for diaObject in diaObjectList:
        diaObjectId = diaObject['diaObjectId']
        t1 = time.time()
        if t1-t0 > 60:
            print('%d objects in %.1f minutes' % (n, (t1-t00)/60))
            t0 = t1

        sources = [dict(s) for s in getDiaSource(diaObjectId)]
        fsources = [dict(s) for s in getForcedSourceOnDiaObject(diaObjectId)]

        obj = {
            'DiaObject'                   : dict(diaObject),
            'DiaSourceList'               : sources,
            'ForcedSourceOnDiaObjectsList': fsources
        }
        f = open(dir + '/%d.json' % diaObjectId, 'w')
        s = json.dumps(obj, indent=2, default=np_encoder)
        f.write(s)
        f.close()
        n += 1
