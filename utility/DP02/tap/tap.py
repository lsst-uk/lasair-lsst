import sys, os, requests, time, settings
import pyvo as pyvo
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
    return DiaSrcs

def getDiaSource(diaObjectId):
    query = """
    SELECT *
    FROM dp02_dc2_catalogs.DiaSource
    WHERE diaObjectId = """ + str(diaObjectId)

    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return DiaSrcs

def getForcedSourceOnDiaObject(diaObjectId):
    query = """
    SELECT *
    FROM dp02_dc2_catalogs.ForcedSourceOnDiaObject
    WHERE diaObjectId = """ + str(diaObjectId)

    results = service.search(query)
    DiaSrcs = results.to_table()
    del results
    return DiaSrcs

if __name__ == '__main__':
    if len(sys.argv) > 2:
        howMany        = int(sys.argv[1])
        howManySources = int(sys.argv[2])
    else:
        howMany = 5
        howManySources = 10

    print('Fetching %d objects with more than %d sources' % (howMany, howManySources))
    dir = '../data/data_%04d_%d' % (howMany, howManySources)
    os.system('mkdir %s' % dir)
    os.system('mkdir %s/diaSource' % dir)
    os.system('mkdir %s/forcedSourceOnDiaObject' % dir)

    objects = getDiaObject(howMany, howManySources)
    ascii.write(objects, dir + '/diaObject.csv', format='csv', overwrite=True)

    diaObjectIdList = objects['diaObjectId']
    t00 = t0 = time.time()
    n = 0
    for diaObjectId in diaObjectIdList:
        t1 = time.time()
        if t1-t0 > 60:
            print('%d objects in %.1f minutes' % (n, (t1-t00)/60))
            t0 = t1
#        print(diaObjectId)

        sources = getDiaSource(diaObjectId)
        ascii.write(sources, dir + '/diaSource/%d.csv'%diaObjectId, \
            format='csv', overwrite=True)

        fsources = getForcedSourceOnDiaObject(diaObjectId)
        ascii.write(sources, dir + '/forcedSourceOnDiaObject/%d.csv'%diaObjectId, \
            format='csv', overwrite=True)
        n += 1
