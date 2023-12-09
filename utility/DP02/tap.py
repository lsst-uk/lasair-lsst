import sys, os, requests, time, settings, json, gzip
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

def getDiaObject(decMin, decMax):
    query = """
    SELECT * FROM dp02_dc2_catalogs.DiaObject 
    WHERE decl > %f AND decl < %f """
    query = query % (decMin, decMax)

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
    query = """SELECT cv.expMidptMJD AS midPointTai, fs.* FROM 
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

def getBatch(diaObjectList, fileOut):
    diaObjectIdList = [int(d['diaObjectId']) for d in diaObjectList]

    sources         = [dict(s) for s in getDiaSource(diaObjectIdList)]
    fsources        = [dict(f) for f in getForcedSourceOnDiaObject(diaObjectIdList)]

#    print('%d/%d/%d objects/sources/forcedsources' % \
#            (len(diaObjectIdList), len(sources), len(fsources)))

    objList = []
    for diaObject in diaObjectList:
        diaObjectId = diaObject['diaObjectId']
        obj = {
            'DiaObject'                  : dict(diaObject),
            'DiaSourceList'              : [s for s in  sources if s['diaObjectId']==diaObjectId],
            'ForcedSourceOnDiaObjectList': [f for f in fsources if f['diaObjectId']==diaObjectId],
        }
        objList.append(obj)

    s = json.dumps(objList, default=np_encoder)
    with gzip.open(fileOut, 'wt', encoding='UTF-8') as zipfile:
        zipfile.write(s)

if __name__ == '__main__':
    batchSize = 50
    if len(sys.argv) > 2:
        decMin        = float(sys.argv[1])
        decMax        = float(sys.argv[2])

    dirOut = 'data/data_%.4f_%.4f' % (-decMin, -decMax)
        
    print('Data going to ', dirOut)
    os.system('mkdir -p %s' % dirOut)

    t0 = time.time()
    diaObjectList = getDiaObject(decMin, decMax)
    nBatch = 1 + len(diaObjectList) // batchSize
    t1 = time.time()
    print('Fetched %d objects in %.1f minutes' % (len(diaObjectList), (t1-t0)/60))
    
    for iBatch in range(nBatch):
        fileOut = dirOut +'/'+ 'batch%04d.json.gz'%iBatch
        mn = iBatch*batchSize
        mx = min((iBatch+1)*batchSize, len(diaObjectList))
        getBatch(diaObjectList[mn:mx], fileOut)
        t1 = time.time()
        print('%.1f minutes: from %d to %d' % ((t1-t0)/60, mn, mx))
