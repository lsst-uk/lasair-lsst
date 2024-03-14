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
sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import mysql.connector


def watchmaps(fltr):
    try:
        hits = get_watchmap_hits(fltr, settings.AREA_MOCS)
    except Exception as e:
        fltr.log.error("ERROR in watchmaps/get_watchmap_hits" + str(e))
        return None

    if len(hits) > 0:
        try:
            insert_watchmap_hits(fltr, hits)
        except Exception as e:
            fltr.log.error("ERROR in watchmaps/insert_watchmap_hits" + str(e))
            return None
    return len(hits)


def get_watchmap_hits(fltr, cache_dir):
    """ get_watchmap_hits.
    Get all the alerts, then run against the watchmaplist, return the hits

    Args:
        fltr:
        cache_dir:
    """
    # read in the cache files
    watchmaplist = read_watchmap_cache_files(cache_dir)

    # get the alert positions from the database
    alertlist = fetch_alerts(fltr)

    # check the list against the watchmaps
    hits = check_alerts_against_watchmaps(fltr, alertlist, watchmaplist)
    return hits


def read_watchmap_cache_files(fltr, cache_dir):
    """
    read_watchmap_cache_files
    This function reads all the files in the cache directories and keeps them in memory
    in a list called "watchmaplist". Each watchmap is a dictionary:
        ar_id: the id from tha database
        moc  : the ingestred moc

    Args:
        fltr:
        cache_dir:
    """
    watchmaplist = []

    try:
        dir_list = os.listdir(cache_dir)
    except Exception as err:
        fltr.log.error('ERROR in watchlists/read_watchmap_cache_files: cannot read watchmap cache directory: %s' % str(err))
        return None

    for ar_file in dir_list:
        # every file in the cache should be of the form ar_<nn>.fits
        # where nn is the area id
        tok = ar_file.split('.')
        if tok[1] != 'fits':
            continue
        try:
            ar_id = int(tok[0][3:])
        except ValueError:
            continue

        gfile = cache_dir + '/' + ar_file
        try:
            moc = MOC.from_fits(gfile)
        except:
            continue
        watchmap = {'ar_id': ar_id, 'moc': moc}
        watchmaplist.append(watchmap)
    return watchmaplist


def check_alerts_against_watchmap(fltr, alertlist, watchmap):
    """ check_alerts_against_watchmap.
    For a given moc, check the alerts in the batch 

    Args:
        fltr:
        alertlist:
        watchmap:
    """
    # alert positions
    alertobjlist = alertlist['obj']
    alertralist = alertlist['ra']
    alertdelist = alertlist['de']

    # here is the crossmatch
    try:
        result = watchmap['moc'].contains(alertralist*u.deg, alertdelist*u.deg)
    except Exception as e:
        fltr.log.error("ERROR in filter/get_watchmap_hits ar_id=%d: %s" % (watchmap['ar_id'], str(e)))
        return []

    hits = []
    # go through the boolean vector, looking for hits
    for ialert in range(len(alertralist)):
        if result[ialert]:
            hits.append({
                        'ar_id': watchmap['ar_id'],
                        'diaObjectId': alertobjlist[ialert]
                    })
    return hits


def check_alerts_against_watchmaps(fltr, alertlist, watchmaplist):
    """ check_alerts_against_watchmaps.
    check the batch of alerts agains all the watchmaps

    Args:
        fltr:
        alertlist:
        watchmaplist:
    """
    hits = []
    for watchmap in watchmaplist:
        hits += check_alerts_against_watchmap(fltr, alertlist, watchmap)
    return hits


def fetch_alerts(fltr, jd=None, limit=None, offset=None):
    """ fetch_alerts.
    Get all the alerts from the local cache to check againstr watchlist

    Args:
        fltr:
        offset:
        limit:
        jd:
    """
    cursor = fltr.database.cursor(buffered=True, dictionary=True)

    query = 'SELECT diaObjectId, ra, decl from objects'
    if jd:
        query += ' WHERE jd>%f ' % jd
    if limit:
        query += ' LIMIT %d OFFSET %d' % (limit, offset)
    cursor.execute(query)
    objlist = []
    ralist = []
    delist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
        ralist.append (row['ra'])
        delist.append (row['decl'])
    return {"obj":objlist, "ra":ralist, "de":delist}


def insert_watchmap_hits(fltr, hits):
    """ insert_watchmap_hits.
    Build and execute the insertion query to get the hits into the database

    Args:
        fltr:
        hits:
    """
    cursor = fltr.database.cursor(buffered=True, dictionary=True)

    query = "REPLACE into area_hits (ar_id, diaObjectId) VALUES\n"
    hitlist = []
    for hit in hits:
        hitlist.append('(%d,"%s")' %  (hit['ar_id'], hit['diaObjectId']))
    query += ',\n'.join(hitlist)
    try:
        cursor.execute(query)
        cursor.close()
    except mysql.connector.Error as err:
        print('ERROR in filter/check_alerts_watchmaps cannot insert watchmaps_hits: %s' % str(err))
        sys.stdout.flush()
    fltr.database.commit()

