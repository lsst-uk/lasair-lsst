"""
watchmaps.py
This code checks a batch of alerts against the cached watchmap files, The files are kept 
in a file named ar_<nn>.fits where nn is the area id from the database. 
The "moc<nnn>.fits" files are
"Multi-Order Coverage maps", https://cds-astro.github.io/mocpy/. 
"""
import os, sys
from mocpy import MOC
import astropy.units as u
from skytag.commonutils import prob_at_location

sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, lasairLogging

CONVERT_Z_TO_DISTANCE = 4348

def mocfilename(gw):
    return '/mnt/cephfs/lasair/mma/gw/%s/%s/90.moc' % (gw['otherId'], gw['version'])

def mapfilename(gw):
    return '/mnt/cephfs/lasair/mma/gw/%s/%s/map.fits' % (gw['otherId'], gw['version'])

def get_watchmap_hits(database, gw):
    """ get_watchmap_hits.
    Get all the alerts, then run against the watchmaplist, return the hits

    Args:
        gw:
        cache_dir:
    """
    moc = MOC.from_fits(mocfilename(gw))

    # get the alert positions from the database
    alertlist = fetch_alerts(database, gw)
    print('found %d alerts between MJD %f and %f' % (len(alertlist), gw['mjdmin'], gw['mjdmax']))

    # check the list against the watchmaps
    skymaphits = check_alerts_against_moc(gw, alertlist, moc)
    return skymaphits

def check_alerts_against_moc(gw, alertlist, moc):
    """ check_alerts_against_watchmap.
    For a given moc, check the alerts in the batch 

    Args:
        gw:
        alertlist:
        watchmap:
    """
    # alert positions
    alertobjlist      = alertlist['obj']
    alertralist       = alertlist['ra']
    alertdelist       = alertlist['de']
    alertdistancelist = alertlist['distance']

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
            distsigma.append(abs(gw_distance - mocdistancelist[i])/gw_diststddev)
        else:
            distsigma.append(None)

    skymaphits = {
        'diaObjectId': mocobjlist, 
        'skyprob'    : skyprob, 
        'distsigma'  : distsigma,
    }
    return skymaphits

def fetch_alerts(database, gw):
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
    query += ' AND maxTai BETWEEN %f AND %f' % (gw['mjdmin'], gw['mjdmax'])
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

def insert_skymap_hits(database, gw, skymaphits):
    """ insert_watchmap_hits.
    Build and execute the insertion query to get the hits into the database

    Args:
        gw:
        hits:
    """
    cursor = database.cursor(buffered=True, dictionary=True)

    print(skymaphits)

    query = "REPLACE into mma_area_hits (wl_id, diaObjectId) VALUES\n"
    hitlist = []
    for hit in skymaphits:   # HACK wl_id
        print(hit)
        hitlist.append('(%d,%d,%f,%f)' %  (20, hit['diaObjectId'], hit['skyprob'], hit['distsigma']))

    query += ',\n'.join(hitlist)
    print(query)

    try:
        cursor.execute(query)
        cursor.close()
    except mysql.connector.Error as err:
        print('ERROR in filter/check_alerts_watchmaps cannot insert watchmaps_hits: %s' % str(err))
        sys.stdout.flush()
    database.commit()

if __name__=="__main__":
    database = db_connect.remote()

    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("mma_watchmap")

    gw = {
        'otherId': 'MS240319j',
        'version': '20240319T094039_preliminary',
        'mjdmin': 100,
        'mjdmax': 1000000,
    }

    skymaphits = get_watchmap_hits(database, gw)
    if len(skymaphits) > 0:
        insert_skymap_hits(database, gw, skymaphits)
