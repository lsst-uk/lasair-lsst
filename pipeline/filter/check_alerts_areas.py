"""
check_alerts_areas.py
This code checks a batch of alerts against the cached area files, The files are kept 
in a file named ar_<nn>.fits where nn is the area id from the database. 
The "moc<nnn>.fits" files are
"Multi-Order Coverage maps", https://cds-astro.github.io/mocpy/. 
"""
import os, sys
import math
from mocpy import MOC
import astropy.units as u
sys.path.append('../../common/src')
import lasairLogging

def read_area_cache_files(cache_dir):
    """
    read_area_cache_files
    This function reads all the files in the cache directories and keeps them in memory
    in a list called "arealist". Each area is a dictionary:
        ar_id: the id from tha database
        moc  : the ingestred moc

    Args:
        cache_dir:
    """
    arealist = []
    for ar_file in os.listdir(cache_dir):
        # every file in the cache should be of the form ar_<nn>.fits
        # where nn is the area id
        tok = ar_file.split('.')
        if tok[1] != 'fits': continue
        try:     ar_id = int(tok[0][3:])
        except:  continue

        gfile = cache_dir + '/' + ar_file
        moc = MOC.from_fits(gfile)
        area = {'ar_id':ar_id, 'moc':moc}
        arealist.append(area)
    return arealist

def check_alerts_against_area(alertlist, area):
    """ check_alerts_against_area.
    For a given moc, check the alerts in the batch 

    Args:
        alertlist:
        area:
    """
    # alert positions
    alertobjlist = alertlist['obj']
    alertralist  = alertlist['ra']
    alertdelist  = alertlist['de']

    # here is the crossmatch
    try:
        result = area['moc'].contains(alertralist*u.deg, alertdelist*u.deg)
    except Exception as e:
        log = lasairLogging.getLogger("filter")
        log.error("ERROR in filter/get_area_hits ar_id=%d: %s" % (area['ar_id'], str(e)))
        return []

    hits = []
    # go through the boolean vector, looking for hits
    for ialert in range(len(alertralist)):
        if(result[ialert]):
            hits.append({
                        'ar_id'   :area['ar_id'], 
                        'diaObjectId':alertobjlist[ialert]
                    })
    return hits

def check_alerts_against_areas(alertlist, arealist):
    """ check_alerts_against_areas.
    check the batch of alerts agains all the areas

    Args:
        alertlist:
        arealist:
    """
    hits = []
    for area in arealist:
        ar_id = area['ar_id']
        hits += check_alerts_against_area(alertlist, area)
    return hits

def fetch_alerts(msl):
    """ fetch_alerts.
    Get all the alerts from the local cache to check againstr watchlist

    Args:
        msl:
    """
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = 'SELECT diaObjectId, ra, decl from diaObjects'
    cursor.execute(query)
    objlist = []
    ralist = []
    delist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
        ralist.append (row['ra'])
        delist.append (row['decl'])
    return {"obj":objlist, "ra":ralist, "de":delist}

def get_area_hits(msl, cache_dir):
    """ get_area_hits.
    Get all the alerts, then run against the arealist, return the hits

    Args:
        msl:
        cache_dir:
    """
    # read in the cache files
    arealist = read_area_cache_files(cache_dir)

    # get the alert positions from the database
    alertlist = fetch_alerts(msl)

    # check the list against the watchlists
    hits = check_alerts_against_areas(alertlist, arealist)
    return hits

def insert_area_hits(msl, hits):
    """ insert_area_hits.
    Build and execute the insertion query to get the hits into the database

    Args:
        msl:
        hits:
    """
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = "REPLACE into area_hits (ar_id, diaObjectId) VALUES\n"
    list = []
    for hit in hits:
        list.append('(%d,"%s")' %  (hit['ar_id'], hit['diaObjectId']))
    query += ',\n'.join(list)
    try:
       cursor.execute(query)
       cursor.close()
    except mysql.connector.Error as err:
       print('ERROR in filter/check_alerts_areas cannot insert areas_hits: %s' % str(err))
       sys.stdout.flush()
    msl.commit()

if __name__ == "__main__":
    import sys
    sys.path.append('../../common')
    import settings
    sys.path.append('../../common/src')
    import db_connect, lasairLogging

    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("filter")

    msl_local = db_connect.local()

    # can run the area process without the rest of the filter code 
    hits = get_area_hits(msl_local, settings.AREA_MOCS)
    if hits:
        for hit in hits: print(hit)
        insert_area_hits(msl_local, hits)
