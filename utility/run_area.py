import sys
from mocpy import MOC
sys.path.append('../common')
import settings
sys.path.append('../common/src')
import db_connect, lasairLogging
sys.path.append('../pipeline/filter')
from check_alerts_areas import check_alerts_against_area
from check_alerts_areas import fetch_alerts, insert_area_hits

def run_area(msl, ar_id):
    """ Delete all the hits and remake.
    """
    cursor  = msl.cursor(buffered=True, dictionary=True)
    query = 'DELETE FROM area_hits WHERE ar_id=%d' % ar_id
    cursor.execute(query)
    msl.commit()

    n_hits = 0

    cache_dir = settings.AREA_MOCS
    gfile = '%s/ar_%d.fits' % (cache_dir, ar_id)
    moc = MOC.from_fits(gfile)
    area = {'ar_id':ar_id, 'moc':moc}
    print('Found MOC for area %d' % ar_id)

    alertlist = fetch_alerts(msl)
    print('Found %d alerts' % len(alertlist['obj']))

    hits = check_alerts_against_area(alertlist, area)
    print('Found %d hits' % len(hits))
    
    insert_area_hits(msl, hits)
    print('Inserted into database')

if __name__ == "__main__":
    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("filter")

    try:
        ar_id = int(sys.argv[1])
    except:
        print('Usage: python3 run_area.py ar_id')
        sys.exit()
    msl = db_connect.remote()
    run_area(msl, ar_id)
