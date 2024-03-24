"""
Run all currently active skymaps against all alerts.

Usage:
    run_skymaps.py [--mw_id=mw_id]
                   [--minmjd=minmjd]
                   [--maxmjd=maxmjd]

Options:
    --mw_id=mw_id      Skymap ID to use or else all in time range
    --minmjd=minmjd    Choose skymaps older than this MJD
    --maxmjd=maxmjd    Choose skymaps younger than this MJD
"""

import sys
import time
from docopt import docopt
sys.path.append('../../../common/src')
import skymaps
import db_connect

if __name__=="__main__":
    args = docopt(__doc__)
#    print(args)
    database = db_connect.remote()

    if args['--maxmjd']: maxmjd = float(args['--maxmjd'])
    else:                maxmjd = skymaps.mjdnow()
    
    if args['--minmjd']: minmjd = float(args['--minmjd'])
    else:                minmjd = maxmjd - settings.GW_ACTIVE_DAYS

    if args['--mw_id']:
        mw_id = int(args['--mw_id'])
        gw = skymaps.fetch_skymap_by_id(database, mw_id)
        skymaplist = [gw]
    else:
        print('searching for skymaps between %f and %f' % (minmjd, maxmjd))
        skymaplist = skymaps.fetch_skymaps_by_mjd(database, minmjd, maxmjd)

    print('found %d active skymaps' % len(skymaplist))

    for gw in skymaplist:
        skymaphits = skymaps.get_skymap_hits(database, gw, minmjd, maxmjd, verbose=True)
        if len(skymaphits['diaObjectId']) > 0:
            nhits = skymaps.insert_skymap_hits(database, gw, skymaphits)
            print('mw_id=%d got %d hits' % (gw['mw_id'], nhits))
        else:
            print('mw_id=%d no hits' % gw['mw_id'])
