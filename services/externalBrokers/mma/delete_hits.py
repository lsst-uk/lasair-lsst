"""
Delete mma_area_hits as specified. BUt not the mma_areas themselves.

Usage:
    delete_hits.py [--mw_id=mw_id]
                   [--minmjd=minmjd]
                   [--maxmjd=maxmjd]

Options:
    --mw_id=mw_id      Skymap ID to use or else all in time range
    --minmjd=minmjd    Choose all skymaps older than this MJD
    --maxmjd=maxmjd    Choose all skymaps younger than this MJD
"""

import sys
import time
from docopt import docopt
sys.path.append('../../../common/src')
import skymaps
import db_connect

if __name__=="__main__":
    args = docopt(__doc__)
    database = db_connect.remote()

    if args['--maxmjd']: mjdmax = float(args['--mjdmax'])
    else:                maxmjd = skymaps.mjdnow()
    
    if args['--minmjd']: minmjd = float(args['--minmjd'])
    else:                minmjd = maxmjd - settings.GW_ACTIVE_DAYS

    if args['--mw_id']:
        mw_id = int(args['--mw_id'])
        skymaplist = [mw_id]
    else:
        print('searching for skymaps between %f and %f' % (minmjd, maxmjd))
        skymaplist = skymaps.fetch_skymaps_by_mjd(database, minmjd, maxmjd)

    print('found %d active skymaps' % len(skymaplist))

    for mw_id in skymaplist:
        ndeleted = skymaps.delete_skymap_hits(database, mw_id)
        print('mw_id %d, deleted %d' % (mw_id, ndeleted))
