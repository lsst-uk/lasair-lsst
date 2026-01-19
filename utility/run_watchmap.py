import sys
from mocpy import MOC
sys.path.append('../common')
import settings
sys.path.append('../common/src')
import db_connect, lasairLogging
sys.path.append('../pipeline/filter')
from watchmaps import check_alerts_against_watchmap
from watchmaps import fetch_alerts, insert_watchmap_hits

def run_watchmap(batch, ar_id):
    """ Delete all the hits and remake.
    """
    cursor  = batch.database.cursor(buffered=True, dictionary=True)
    query = 'DELETE FROM area_hits WHERE ar_id=%d' % ar_id
    cursor.execute(query)
    batch.database.commit()

    n_hits = 0

    cache_dir = settings.AREA_MOCS
    gfile = '%s/ar_%d.fits' % (cache_dir, ar_id)
    moc = MOC.from_fits(gfile)
    watchmap = {'ar_id':ar_id, 'moc':moc}
    print('Found MOC for watchmap %d' % ar_id)

    # runs out of memory with the whole database
    npage = 100000
    for ipage in range(100):
        alertlist = fetch_alerts(batch, limit=npage, offset=ipage*npage)
        nalert = len(alertlist['obj'])
        if nalert == 0:
            break
        print('Found %d alerts' % nalert)

        hits = check_alerts_against_watchmap(batch, alertlist, watchmap)
        print('Found %d hits' % len(hits))
    
        insert_watchmap_hits(batch, hits)
        print('Inserted into database')

# A way to pass the db connection to the watchmap code
class Batch():
    def __init__(self):
        self.database = db_connect.remote()

if __name__ == "__main__":
    batch = Batch()

    try:
        ar_id = int(sys.argv[1])
    except:
        print('Usage: python3 run_watchmap.py ar_id')
        sys.exit()
    run_watchmap(batch, ar_id)
