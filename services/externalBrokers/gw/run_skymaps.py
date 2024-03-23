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
    database = db_connect.remote()

    if args['--maxmjd']: mjdmax = float(args['--mjdmax'])
    else:                maxmjd = skymaps.mjdnow()
    
    if args['--minmjd']: minmjd = float(args['--minmjd'])
    else:                minmjd = maxmjd - 21 # three weeks

    if args['--mw_id']:
        mw_id = int(args['--mw_id'])
        skymaplist = [mw_id]
    else:
        print('searching for skymaps between %f and %f' % (minmjd, maxmjd))
        skymaplist = skymaps.fetch_skymaps_by_mjd(database, minmjd, maxmjd)

    print('found %d active skymaps' % len(skymaplist))

    for mw_id in skymaplist:
        print('mw_id=', mw_id)
        gw = skymaps.fetch_skymap_by_id(database, mw_id)
        skymaphits = skymaps.get_skymap_hits(database, gw, minmjd, maxmjd)
        if len(skymaphits['diaObjectId']) > 0:
            skymaps.insert_skymap_hits(database, gw, skymaphits)
