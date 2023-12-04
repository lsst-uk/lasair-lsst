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

def getDiaSource(diaObjectIdList):
    query = """
    SELECT *
    FROM dp02_dc2_catalogs.DiaSource
    WHERE diaObjectId in (%s)""" % ','.join([str(d) for d in diaObjectIdList])
    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return list(DiaSrcs)

def getForcedSourceOnDiaObject(diaObjectIdList):
    query = """SELECT cv.expMidptMJD AS midPointTai, cv.band as filterName, 
    fs.* FROM 
    dp02_dc2_catalogs.ForcedSourceOnDiaObject as fs 
    JOIN dp02_dc2_catalogs.CcdVisit as cv 
    ON cv.CcdVisitId=fs.CcdVisitId 
    WHERE fs.diaObjectId IN (%s)""" % ','.join([str(d) for d in diaObjectIdList])
    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return list(DiaSrcs)

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

def getBatch(diaObjectList):
    dir = 'data/data_%06d_%d' % (howMany, howManySources)
    diaObjectIdList = [int(d['diaObjectId']) for d in diaObjectList]

    sources = []
    for s in getDiaSource(diaObjectIdList):
        # some fluxes are None for some reason
        if s['psFlux'] is None: continue
        ds = dict(s)
        sources.append(ds)

    fsources = []
    for f in getForcedSourceOnDiaObject(diaObjectIdList):
        # some fluxes are None for some reason
        if f['psfFlux'] is None: continue
        df = dict(f)
        # forced source has psfFlux but source has psFlux
        df['psFlux']    = df['psfFlux']
        df['psFluxErr'] = df['psfFluxErr']
        del df['psfFlux']
        del df['psFluxErr']
        fsources.append(df)
    print('%d/%d/%d objects/sources/forcedsources' % \
            (len(diaObjectIdList), len(sources), len(fsources)))

    for diaObject in diaObjectList:
        diaObjectId = diaObject['diaObjectId']
        obj = {
            'DiaObject'                  : dict(diaObject),
            'DiaSourceList'              : [s for s in  sources if s['diaObjectId']==diaObjectId],
            'ForcedSourceOnDiaObjectList': [f for f in fsources if f['diaObjectId']==diaObjectId],
        }
        f = open(dir + '/%d.json' % diaObjectId, 'w')
        s = json.dumps(obj, indent=2, default=np_encoder)
        f.write(s)
        f.close()

if __name__ == '__main__':
    batchSize = 10
    if len(sys.argv) > 2:
        howMany        = int(sys.argv[1])
        howManySources = int(sys.argv[2])
    else:
        howMany = 5
        howManySources = 10

    if howMany < batchSize:
        nBatch = 1
        batchSize = howMany
    else:
        nBatch = howMany//batchSize
        howMany = nBatch*batchSize
        
    print('Fetching %d objects with more than %d sources' % (howMany, howManySources))
    dir = 'data/data_%06d_%d' % (howMany, howManySources)
    os.system('mkdir -p %s' % dir)

    t0 = time.time()
    diaObjectList = getDiaObject(howMany, howManySources)
    t1 = time.time()
    print('Fetched %d objects in %.1f minutes' % (len(diaObjectList), (t1-t0)/60))
    
    t0 = time.time()
    for iBatch in range(nBatch):
        getBatch(diaObjectList[iBatch*batchSize:(iBatch+1)*batchSize])
        t1 = time.time()
        print('%d objects in %.1f minutes' % ((iBatch+1)*batchSize, (t1-t0)/60))
