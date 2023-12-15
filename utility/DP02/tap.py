""" tap.py
Code to pull down DP0.2 from the Rubin RSP using the API.
It takes a range of Dec, for example decMin=-30.1 ro DecMax=-30.0
where DP0.2 is from about -45 to -25
It gets all the diaObjects between the limits, 
then all the diaSources after MJD=61000, and all the forced sources after MJD=61000
Note the finicky join to get the time of the forced source.
You will need a RSP token, whhc should go into a settings.py file that has a line
RSP_TOKEN = 'xxxx'
"""
import sys, os, requests, time, settings, json, gzip
import pyvo as pyvo
import numpy as np
import settings

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
    WHERE midPointTai>61000 AND
    diaObjectId in (%s)""" % ','.join([str(d) for d in diaObjectIdList])
    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return list(DiaSrcs)

def getForcedSourceOnDiaObject(diaObjectIdList):
    query = """SELECT cv.expMidptMJD AS midPointTai, fs.* FROM 
    dp02_dc2_catalogs.ForcedSourceOnDiaObject as fs 
    JOIN dp02_dc2_catalogs.CcdVisit as cv 
    ON cv.CcdVisitId=fs.CcdVisitId 
    WHERE cv.expMidptMJD>61000 AND
    fs.diaObjectId IN (%s)""" % ','.join([str(d) for d in diaObjectIdList])
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
        # don't want objects with no detections
        if len(obj['DiaSourceList']) > 0:
            objList.append(obj)

    s = json.dumps(objList, default=np_encoder)
    with gzip.open(fileOut, 'wt', encoding='UTF-8') as zipfile:
        zipfile.write(s)

#############################################
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('Usage: tap.py <directory> <decMin> <decMax> ')
        sys.exit()
    else:
        decMin    = float(sys.argv[2])
        decMax    = float(sys.argv[3])
        dirOut = sys.argv[1] + '/data_%.4f_%.4f' % (-decMin, -decMax)
        
    # this batchsize is carefully chosen so the pyvo doesn't fail
    batchSize = 200
    print('Data going to %s with dec %f to %f' % (dirOut, decMin, decMax))
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
