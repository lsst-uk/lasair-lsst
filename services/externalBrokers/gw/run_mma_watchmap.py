"""
watchmaps.py
This code checks a batch of alerts against the cached watchmap files, The files are kept 
in a file named ar_<nn>.fits where nn is the area id from the database. 
The "moc<nnn>.fits" files are
"Multi-Order Coverage maps", https://cds-astro.github.io/mocpy/. 
"""
import os, sys, time, math
from mocpy import MOC
import astropy.units as u
from skytag.commonutils import prob_at_location

sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, lasairLogging

CONVERT_Z_TO_DISTANCE = 4348
EXPIRE_DAYS           = 25  # three weeks

def mocfilename(gw):
    filename = '/mnt/cephfs/lasair/mma/gw/%s/%s/90.moc' % (gw['otherId'], gw['version'])
#    print('moc file = ', filename)
    return filename

def mapfilename(gw):
    filename = '/mnt/cephfs/lasair/mma/gw/%s/%s/map.fits' % (gw['otherId'], gw['version'])
#    print('map file = ', filename)
    return filename

def fetch_alerts(database, gw, mjdmin=None, mjdmax=None):
    """ fetch_alerts_sherlock.
    Get all the alerts from the local cache to check againstr watchlist

    Args:
        gw:
        offset:
        limit:
        mjdmax:
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
        if row['distance']:
            distancelist.append(row['distance'])
        elif row['z']:
            distancelist.append(row['z'] * CONVERT_Z_TO_DISTANCE)
        elif row['photoz']:
            distancelist.append(row['photoz'] * CONVERT_Z_TO_DISTANCE)
        else:
            distancelist.append(None)

    return {"obj": objlist, "ra":ralist, "de":delist, \
            "distance":distancelist}

def get_skymap_hits(database, gw, mjdmin=None, mjdmax=None):
    """ get_watchmap_hits.
    Get all the alerts, then run against the watchmaplist, return the hits

    Args:
        gw:
        cache_dir:
    """
    moc = MOC.from_fits(mocfilename(gw))

    # get the alert positions from the database
    alertlist = fetch_alerts(database, gw, mjdmin, mjdmax)

    # alert positions
    alertobjlist      = alertlist['obj']
    alertralist       = alertlist['ra']
    alertdelist       = alertlist['de']
    alertdistancelist = alertlist['distance']

    if mjdmin and mjdmax:
        print('found %d alerts between MJD %f and %f' % (len(alertobjlist), mjdmin, mjdmax))
    else:
        print('found %d alerts ' % len(alertobjlist))

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

    skyprob, gw_disttuples = prob_at_location(
        ra =mocralist,
        dec=mocdelist,
        mapPath=mapfilename(gw),
        distance=True
    )
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
    """ insert_watchmap_hits.
    Build and execute the insertion query to get the hits into the database

    Args:
        gw:
        hits:
    """
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

def mjdnow():
    return time.time()/86400 + 40587.0;

def fetch_active_skymaps(database, mjdnow):
    cursor = database.cursor(buffered=True, dictionary=True)
    query = 'SELECT mw_id, event_tai, otherId, version FROM mma_areas '
    query += 'WHERE event_tai > %f' % (mjdnow - EXPIRE_DAYS)
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

if __name__=="__main__":
    database = db_connect.remote()

    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("mma_watchmap")

    active_gw = fetch_active_skymaps(database, mjdnow())
    print('found %d active skymaps' % len(active_gw))
    for gw in active_gw:
        print('\n', gw['otherId'], gw['version'])

        mjdmin = 100
        mjdmax = 1000000
        skymaphits = get_skymap_hits(database, gw, mjdmin, mjdmax)

        if len(skymaphits['diaObjectId']) > 0:
            insert_skymap_hits(database, gw, skymaphits)
