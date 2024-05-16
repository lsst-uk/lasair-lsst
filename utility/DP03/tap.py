""" tap.py
Code to pull down DP0.2 from the Rubin RSP using the API.
It takes a range of Dec, for example mjdMin=-30.1 ro DecMax=-30.0
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
import numpy.ma as ma
import settings

url = 'https://data.lsst.cloud/api/ssotap'

session = requests.Session()
session.headers["Authorization"] = "Bearer " + settings.RSP_TOKEN
auth = pyvo.auth.authsession.AuthSession()
auth.credentials.set("lsst-token", session)
auth.add_security_method_for_url(url, "lsst-token")
auth.add_security_method_for_url(url + "/sync", "lsst-token")
auth.add_security_method_for_url(url + "/async", "lsst-token")
auth.add_security_method_for_url(url + "/tables", "lsst-token")

service = pyvo.dal.TAPService(url, auth)

def getSSObject(mjdMin, mjdMax):
    query = """
    SELECT * FROM dp03_catalogs_10yr.SSObject
    WHERE discoverySubmissionDate > %f AND discoverySubmissionDate < %f """
    query = query % (mjdMin, mjdMax)

    results = service.search(query)
    ssSrcs = results.to_table()
    del results
    return list(ssSrcs)

def getMPCORB(ssObjectIdList):
    query = """
    SELECT * FROM dp03_catalogs_10yr.MPCORB WHERE
    SSObjectId in (%s)""" % ','.join([str(d) for d in ssObjectIdList])
    results = service.search(query)
    MPCORBs = results.to_table()
    del results
    return list(MPCORBs)

def getDiaSources(ssObjectIdList):
    query = """SELECT * FROM dp03_catalogs_10yr.diaSource WHERE
    ssObjectId IN (%s)""" % ','.join([str(d) for d in ssObjectIdList])
    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return list(DiaSrcs)

def getSSSources(ssObjectIdList):
    query = """SELECT * FROM dp03_catalogs_10yr.SSSource WHERE
    ssObjectId IN (%s)""" % ','.join([str(d) for d in ssObjectIdList])
    results = service.search(query)
    SsSrcs = results.to_table()
    del results
    return list(SsSrcs)

def np_encoder(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ma.MaskedArray):
        return ma.MaskedArray.__float__(obj) 

def getBatch(ssObjectList, fileOut):
    ssObjectIdList = [int(d['ssObjectId']) for d in ssObjectList]

    MPCORBs          = [dict(s) for s in getMPCORB(ssObjectIdList)]
    diaSources       = [dict(s) for s in getDiaSources(ssObjectIdList)]
    ssSources        = [dict(s) for s in getSSSources(ssObjectIdList)]

#### Change to a Lasair/MySQL convention. 
#    "dec" is a reserved word in MySQL, it would be a nest of error.
#    so we use "decl"
    for diaSource in diaSources:  ### HACK
        diaSource['decl'] = diaSource['dec']
        del diaSource['dec']

    print('%d/%d/%d objects/diasources/sssources' % \
            (len(ssObjectIdList), len(diaSources), len(ssSources)))

    objList = []
    for ssObject in ssObjectList:
        ssObjectId = ssObject['ssObjectId']
        MPC = [m for m in  MPCORBs if m['ssObjectId']==ssObjectId]
        if len(MPC) == 0:
            continue
        obj = {
            'SSObjectId'     : ssObjectId,
            'SSObject'       : dict(ssObject),
            'MPCORB'         : dict(MPC[0]),
            'DiaSourceList'  : [s for s in  diaSources if s['ssObjectId']==ssObjectId],
            'SSSourceList'   : [f for f in ssSources if f['ssObjectId']==ssObjectId],
        }
        # don't want objects with no detections
        if len(obj['SSSourceList']) > 0:
            objList.append(obj)

    s = json.dumps(objList, default=np_encoder)
    with gzip.open(fileOut, 'wt', encoding='UTF-8') as zipfile:
        zipfile.write(s)

#############################################
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('Usage: tap.py <directory> <mjdMin> <mjdMax> ')
        sys.exit()
    else:
        mjdMin    = float(sys.argv[2])
        mjdMax    = float(sys.argv[3])
        dirOut = sys.argv[1] + '/data_%.0f_%.0f' % (mjdMin, mjdMax)
        
    # this batchsize is carefully chosen so the pyvo doesn't fail
    batchSize = 200
    print('Data going to %s with mjd %f to %f' % (dirOut, mjdMin, mjdMax))
    os.system('mkdir -p %s' % dirOut)

    t0 = time.time()
    ssObjectList = getSSObject(mjdMin, mjdMax)
    print('got ', len(ssObjectList))

    nBatch = 1 + len(ssObjectList) // batchSize
    t1 = time.time()
    print('Fetched %d objects in %.1f minutes' % (len(ssObjectList), (t1-t0)/60))
    
    for iBatch in range(nBatch):
        fileOut = dirOut +'/'+ 'batch%04d.json.gz'%iBatch
        mn = iBatch*batchSize
        mx = min((iBatch+1)*batchSize, len(ssObjectList))
        getBatch(ssObjectList[mn:mx], fileOut)
        t1 = time.time()
        print('%.1f minutes: %d done of %d' % ((t1-t0)/60, mx, len(ssObjectList)))
