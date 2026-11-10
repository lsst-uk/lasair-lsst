"""
skymaps.py
This code checks a batch of alerts against the cached mma_watchmap files, 
The skymap- and 3 MOC files are kept in the CephFS.
"""
import os
import sys 
import time
import math
import json
from mocpy import MOC
import astropy.units as u
from skytag.commonutils import prob_at_location
import healpy as hp
import numpy as np

sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, lasairLogging

def get_skymap_hits(database, namespace, mma_event, mjdmin=None, mjdmax=None, verbose=False):
    """ Get all the alerts that match a given skymap, 
        then run against the watchmaplist, return the hits
    """
    event_id  = mma_event['event_id']
    event_tai = mma_event['event_tai']
    if 'mocfilename' in mma_event:
        moc = MOC.from_fits(mma_event['mocfilename'])
    else:
        moc = MOC.from_fits(mocfilename(namespace, mma_event))

    # get the alert positions from the database
    alertlist = fetch_alerts(database, mma_event, mjdmin, mjdmax, verbose)

    # alert positions
    alertobjlist      = alertlist['obj']
    alertralist       = alertlist['ra']
    alertdelist       = alertlist['de']
    alertdtlist       = [f - event_tai for f in alertlist['first_mjd']]
    alertdistancelist = alertlist['distance']

    if verbose:
        print('found %d alerts ' % len(alertobjlist))

    # here is the crossmatch
    result = moc.contains_lonlat(alertralist * u.deg, alertdelist * u.deg)

    mocralist = []
    mocdelist = []
    mocdtlist = []
    mocobjlist   = []
    mocdistancelist   = []
    # go through the boolean vector, looking for hits
    for ialert in range(len(alertralist)):
        if result[ialert]:
            mocobjlist     .append(alertobjlist[ialert])
            mocralist      .append(alertralist[ialert])
            mocdelist      .append(alertdelist[ialert])
            mocdtlist      .append(alertdtlist[ialert])
            mocdistancelist.append(alertdistancelist[ialert])

#    if verbose:
#        print(mocralist, mocdelist, mocdtlist, mocdistancelist)

    if namespace == 'LVK':
        # contour is the contour of the skymap on which the given point lies
        # gw_disttuples are pairs of (mean,stddev) on the diatance
        # the code is at https://skytag.readthedocs.io/
        if 'mapfilename' in mma_event:
            map = mma_event['mapfilename']
        else:
            map = mapfilename(namespace, mma_event)

        contour, gw_disttuples, probdens2 = prob_at_location(
            ra =mocralist,
            dec=mocdelist,
            mapPath=map,
            distance=True,
            probdensity=True
        )

        # Use the distance of the optical event, if we have it, to get the
        # number of sigma away from the GW mean distance
        paramslist = []
        distance = []
        for i in range(len(mocobjlist)):
            (gw_distance, gw_diststddev) = gw_disttuples[i]
            if mocdistancelist[i]:
                ds = abs(gw_distance - mocdistancelist[i])/gw_diststddev
                if math.isinf(ds) or ds > 100: ds = 100
                paramslist.append({'dist_mean': gw_distance, 'dist_stddev':gw_diststddev})
                distance.append(mocdistancelist[i])
            else:
                paramslist.append({})
                distance.append(None)

    elif namespace == 'ICC' or namespace == 'ICGB':
        m = hp.read_map(mapfilename(namespace, mma_event))
        total = m.sum()
        m /= total
        theta = np.radians(90.0 - np.array(mocdelist))
        phi = np.radians(np.array(mocralist))
        ipix = hp.ang2pix(hp.get_nside(m), theta, phi)
        probdens2 = m[ipix]
        n = len(probdens2)

        contour = []
        for i in range(n):
            c = np.sum(m[m > probdens2[i]])
            contour.append(c)
            
        paramslist = [{}]*n
        contour = np.array(contour)
        distance  = np.array([None]*n)

    else:
        print(f'Unknown Event namespace {namespace}. Quitting')
        return None

    skymaphits = {
        'diaObjectId': mocobjlist, 
        'event_id'   : event_id,
        'delta_t'    : mocdtlist,
        'contour'    : contour, 
        'distance'   : distance, 
        'probdens2'  : probdens2,
        'paramslist'  : paramslist,
    }
    if verbose:
        print('get_skymap_hits: got %d' % len(skymaphits['diaObjectId']))
    return skymaphits

def fetch_alerts(database, gw, mjdmin=None, mjdmax=None, verbose=False):
    """ Fetch optical alerts and sherlock to check against skymaps
        between two times
    """
    cursor = database.cursor(buffered=True, dictionary=True)

    query = 'SELECT objects.diaObjectId, firstDiaSourceMjdTai, ra, decl, best_distance '
    query += ' FROM objects,sherlock_classifications '
    query += ' WHERE objects.diaObjectId=sherlock_classifications.diaObjectId '
    if mjdmin and mjdmax:
        query += ' AND lastDiaSourceMjdTai BETWEEN %f AND %f' % (mjdmin, mjdmax)
    cursor.execute(query)

    objlist = []
    ralist = []
    delist = []
    first_mjd = []
    distancelist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
        ralist.append(row['ra'])
        delist.append(row['decl'])
        first_mjd.append(row['firstDiaSourceMjdTai'])
        distancelist.append(row['best_distance'])
    if verbose:
        print('fetch_alerts: mjd %s to %s, found %d' % (str(mjdmin), str(mjdmax), len(objlist)))

    return {"obj": objlist, "ra":ralist, "de":delist, "first_mjd":first_mjd, "distance":distancelist}

def fetch_skymaps_by_mjd(database, mjdmin, mjdmax, verbose=False):
    cursor = database.cursor(buffered=True, dictionary=True)
    query = 'SELECT mw_id, namespace, event_tai, area90, event_id, version, params FROM mma_events '
    query += 'WHERE event_tai BETWEEN %f AND %f' % (mjdmin, mjdmax)
    result = []
    try:
        cursor.execute(query)
        for row in cursor:
            result.append(row)
        cursor.close()
        if verbose:
            print('fetch_skymaps_by_mjd: found %d' % len(result))
        return result
    except Exception as e:
        print('ERROR in fetch_active_skymaps cannot query database: %s' % str(e))
        return []

def fetch_skymap_by_id(database, mw_id):
    """ Fetches the GW information for a given ID
    """
    cursor = database.cursor(buffered=True, dictionary=True)
    query = 'SELECT mw_id, event_tai, area90, event_id, version, params FROM mma_events '
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

def insert_skymap_hits(database, mma_event, skymaphits, verbose=False):
    """ Insert skymap hits into the database
    Build and execute the insertion query to get the hits into the database
    """
    cursor = database.cursor(buffered=True, dictionary=True)
    event_id = mma_event['event_id']

    query = "REPLACE into mma_assoc "
    query += "(mw_id, event_id, delta_t, diaObjectId, contour, dist_host, probdens2, params) VALUES\n"
    fmt = "(%d,'%s',%.2f,%d,%s,%s,%s,'%s')"

    hitlist  = []
    mw_id    = mma_event['mw_id']
    dt       = skymaphits['delta_t']
    did      = skymaphits['diaObjectId']
    contours = skymaphits['contour']
    dist     = skymaphits['distance']
    p2       = skymaphits['probdens2']
    paramslist      = skymaphits['paramslist']
    for (delta_t, diaObjectId, contour, distance, probdens2, params) \
            in zip(dt, did, contours, dist, p2, paramslist):
        if contour:   contour   = '%.2f'%contour
        else:         contour   = 'NULL'
        if distance:  dist_host  = '%.2f'%distance
        else:         dist_host  = 'NULL'
        if probdens2: probdens2 = '%.2f'%probdens2
        else:         probdens2 = 'NULL'
        p = (mw_id, event_id, delta_t, diaObjectId, contour, dist_host, probdens2, json.dumps(params))
        hitlist.append(fmt % p)

    query += ',\n'.join(hitlist)

    try:
        cursor.execute(query)
        cursor.close()
        database.commit()
    except Exception as e:
        print('ERROR in insert_skymap_hits cannot insert: %s' % str(e))
        print(query)
    return len(did)

def delete_skymap_hits(database, mw_id):
    """ Delete all hits from this skymap
    """
    cursor = database.cursor(buffered=True, dictionary=True)
    query = 'SELECT count(*) as ndeleted FROM mma_assoc WHERE mw_id=%d' % mw_id
    cursor.execute(query)
    for row in cursor:
        ndeleted = row['ndeleted']

    query = 'DELETE FROM mma_assoc WHERE mw_id=%d' % mw_id
    cursor.execute(query)
    return ndeleted

def mjdnow():
    """ Current MJD 
    """
    return time.time()/86400 + 40587.0;

def mocfilename(namespace, mma_event):
    """ Where to find the 90% MOC for a given skymap and version
    """
    filename = f'{settings.MMA_DIRECTORY}/{namespace}/{mma_event['event_id']}/{mma_event['version']}/90.moc'
    return filename

def mapfilename(namespace, mma_event):
    """ Where to find the skymap file for a given skymap and version
    """
    filename = f'{settings.MMA_DIRECTORY}/{namespace}/{mma_event['event_id']}/{mma_event['version']}/map.fits'
    return filename
