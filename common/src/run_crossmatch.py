import sys
sys.path.append('../common')
import math
import settings
from src import db_connect
from gkhtm import _gkhtm as htmCircle

def distance(ra1, de1, ra2, de2):
    dra = (ra1 - ra2)*math.cos(de1*math.pi/180)
    dde = (de1 - de2)
    return math.sqrt(dra*dra + dde*dde)

def run_crossmatch(msl, radius, wl_id):
    """ Delete all the hits and remake.
    """
    cursor  = msl.cursor(buffered=True, dictionary=True)
    query = 'DELETE FROM watchlist_hits WHERE wl_id=%d' % wl_id
    cursor.execute(query)
    msl.commit()

    n_cones = 0
    n_hits = 0
    # get all the cones and run them
    query = 'SELECT cone_id, ra,decl, name FROM watchlist_cones WHERE wl_id=%d' % wl_id
    cursor.execute(query)
    for row in cursor:
        n_cones += 1
        n_hits += crossmatch(msl, wl_id, row['cone_id'], row['ra'], row['decl'], row['name'], radius)
    print("%d cones, %d hits" % (n_cones, n_hits))
    return n_hits

def crossmatch(msl, wl_id, cone_id, myRA, myDecl, name, radius):
    cursor2 = msl.cursor(buffered=True, dictionary=True)
    cursor3 = msl.cursor(buffered=True, dictionary=True)
    subClause = htmCircle.htmCircleRegion(16, myRA, myDecl, radius)
    subClause = subClause.replace('htm16ID', 'htm16')
    query2 = 'SELECT * FROM objects WHERE htm16 ' + subClause[14: -2]
#    print(query2)
    cursor2.execute(query2)
    n_hits = 0
    for row in cursor2:
        objectId = row['objectId']
        arcsec = 3600*distance(myRA, myDecl, row['ramean'], row['decmean'])
        if arcsec > radius:
            continue
        n_hits += 1
        query3 = "INSERT INTO watchlist_hits (wl_id, cone_id, objectId, arcsec, name) VALUES\n"
        query3 += ' (%d, %d, "%s", %.2f, "%s")' % (wl_id, cone_id, objectId, arcsec, name)
        try:
            cursor3.execute(query3)
            msl.commit()
        except:
            print('%s already matched with %s' % (objectId, name))
    return n_hits

if __name__ == "__main__":
    try:
        wl_id = int(sys.argv[1])
    except:
        print('Usage: python3 run_crossmatch.py wl_id')
        sys.exit()
    radius = 3  # arcseconds
    msl = db_connect.remote()
    run_crossmatch(msl, radius, wl_id)
