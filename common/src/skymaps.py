"""
skymaps.py
This code checks a batch of alerts against the cached mma_watchmap files, 
The skymap- and 3 MOC files are kept in the CephFS.
"""
import os
import sys 
import time
import math
from mocpy import MOC
import astropy.units as u
from skytag.commonutils import prob_at_location

sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, lasairLogging

# This is c/H, speed of light over Hubble constant
CONVERT_Z_TO_DISTANCE = 4271

def mjdnow():
    """ Current MJD 
    """
    return time.time()/86400 + 40587.0;

def mocfilename(gw):
    """ Where to find the 90% MOC for a given skymap and version
    """
    filename = '%s/%s/%s/90.moc' % (settings.GW_DIRECTORY, gw['otherId'], gw['version'])
    return filename

def mapfilename(gw):
    """ Where to find the skymap file for a given skymap and version
    """
    filename = '%s/%s/%s/map.fits' % (settings.GW_DIRECTORY, gw['otherId'], gw['version'])
    return filename

def fetch_alerts(database, gw, mjdmin=None, mjdmax=None):
    """ Fetch optical alerts and sherlock to check against skymaps
        between two times
    """
    cursor = database.cursor(buffered=True, dictionary=True)

    query = 'SELECT objects.diaObjectId, ra, decl, z, photoz, distance '
    query += ' FROM objects,sherlock_classifications '
    query += ' WHERE objects.diaObjectId=sherlock_classifications.diaObjectId '
    if mjdmin and mjdmax:
        query += ' AND maxTai BETWEEN %f AND %f' % (mjdmin, mjdmax)
    cursor.execute(query)

    objlist = []
    ralist = []
    delist = []
    distancelist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
        ralist.append(row['ra'])
        delist.append(row['decl'])

        # The sherlock may have distance in Mpc, z, and/or photoZ
        # distance is best, else z, else photoZ

        if row['distance']:   d = row['distance']
        elif row['z']:        d = row['z']      * CONVERT_Z_TO_DISTANCE
        elif row['photoz']:   d = row['photoz'] * CONVERT_Z_TO_DISTANCE
        else:                 d = None

        distancelist.append(d)

    return {"obj": objlist, "ra":ralist, "de":delist, "distance":distancelist}

def get_skymap_hits(database, gw, mjdmin=None, mjdmax=None):
    """ Get all the alerts that match a given skymap, 
        then run against the watchmaplist, return the hits
    """
    moc = MOC.from_fits(mocfilename(gw))

    # get the alert positions from the database
    alertlist = fetch_alerts(database, gw, mjdmin, mjdmax)

    # alert positions
    alertobjlist      = alertlist['obj']
    alertralist       = alertlist['ra']
    alertdelist       = alertlist['de']
    alertdistancelist = alertlist['distance']

#    if mjdmin and mjdmax:
#        print('found %d alerts between MJD %f and %f' % (len(alertobjlist), mjdmin, mjdmax))
#    else:
#        print('found %d alerts ' % len(alertobjlist))

    # here is the crossmatch
    result = moc.contains_lonlat(alertralist * u.deg, alertdelist * u.deg)

    mocralist = []
    mocdelist = []
    mocobjlist   = []
    mocdistancelist   = []
    # go through the boolean vector, looking for hits
    for ialert in range(len(alertralist)):
        if result[ialert]:
            mocobjlist     .append(alertobjlist[ialert])
            mocralist      .append(alertralist[ialert])
            mocdelist      .append(alertralist[ialert])
            mocdistancelist.append(alertdistancelist[ialert])

    # skyprob is the contour of the skymap on which the given point lies
    # gw_disttuples are pairs of (mean,stddev) on the diatance
    # the code is at https://skytag.readthedocs.io/
    skyprob, gw_disttuples = prob_at_location(
        ra =mocralist,
        dec=mocdelist,
        mapPath=mapfilename(gw),
        distance=True
    )

    # Use the distance of the optical event, if we have it, to get the
    # number of sigma away from the GW mean distance
    distsigma = []
    for i in range(len(mocobjlist)):
        (gw_distance, gw_diststddev) = gw_disttuples[i]
        if mocdistancelist[i]:
            ds = abs(gw_distance - mocdistancelist[i])/gw_diststddev
            if math.isinf(ds): ds = 100
            distsigma.append(ds)
        else:
            distsigma.append(None)

    skymaphits = {
        'diaObjectId': mocobjlist, 
        'skyprob'    : skyprob, 
        'distsigma'  : distsigma,
    }
    return skymaphits

def insert_skymap_hits(database, gw, skymaphits):
    """ Insert skymap hits into the database
    Build and execute the insertion query to get the hits into the database
    """"
    cursor = database.cursor(buffered=True, dictionary=True)

    query = "REPLACE into mma_area_hits (mw_id, diaObjectId, skyprob, distsigma) VALUES\n"
    hitlist = []
    mw_id = gw['mw_id']
    did  = skymaphits['diaObjectId']
    sky  = skymaphits['skyprob']
    dist = skymaphits['distsigma']
    print('inserting %d skymap hits' % len(did))
    for (diaObjectId, skyprob, distsigma) in zip(did, sky, dist):
        if distsigma: distsigma = '%.2f'%distsigma
        else:         distsigma = 'NULL'
        hitlist.append('(%d,%d,%.4f,%s)' %  (mw_id, diaObjectId, skyprob, distsigma))

    query += ',\n'.join(hitlist)

    try:
        cursor.execute(query)
        cursor.close()
        database.commit()
    except Exception as e:
        print('ERROR in insert_skymap_hits cannot insert: %s' % str(e))
        print(query)

def fetch_skymaps_by_mjd(database, mjdmin, mjdmax):
    cursor = database.cursor(buffered=True, dictionary=True)
    query = 'SELECT mw_id, event_tai, area90, otherId, version, params FROM mma_areas '
    query += 'WHERE event_tai BETWEEN %f AND %f' % (mjdmin, mjdmax)
    result = []
    try:
        cursor.execute(query)
        for row in cursor:
            result.append(row)
        cursor.close()
        return result
    except Exception as e:
        print('ERROR in fetch_active_skymaps cannot query database: %s' % str(e))
        return None

def fetch_skymap_by_id(database, mw_id):
    """ Fetches the GW information for a given ID
    """
    cursor = database.cursor(buffered=True, dictionary=True)
    query = 'SELECT mw_id, event_tai, area90, otherId, version, params FROM mma_areas '
    query += 'WHERE mw_id=%d' % mw_id
    try:
        cursor.execute(query)
        for row in cursor:
            return(row)
        cursor.close()
        return result
    except Exception as e:
        print('ERROR in fetch_active_skymaps cannot query database: %s' % str(e))
        return None
