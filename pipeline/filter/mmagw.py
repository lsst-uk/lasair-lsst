"""
mmagw.py
This code checks a batch of alerts against the active GW alerts.
The minmjd,maxmjd are only used during testing.

Usage:
    mmagw.py [--minmjd=minmjd]
             [--maxmjd=maxmjd]

Options:
    --minmjd=minmjd    Choose all skymaps older than this MJD
    --maxmjd=maxmjd    Choose all skymaps younger than this MJD
"""
import os, sys
sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import db_connect, lasairLogging, skymaps


def mmagw(fltr, minmjd=None, maxmjd=None, verbose=False):
    if not maxmjd: 
        maxmjd = skymaps.mjdnow()
    if not minmjd: 
        minmjd = maxmjd - settings.GW_ACTIVE_DAYS

    # must use main database, since GW alert may have been inserted since sunset
    main_database = db_connect.remote()

    try:
        skymaplist = skymaps.fetch_skymaps_by_mjd(main_database, minmjd, maxmjd, verbose)
    except Exception as e:
        fltr.log.error("ERROR in mmagw/mmagw" + str(e))
        return None

    totalnhits = 0
    for gw in skymaplist:
        skymaphits = skymaps.get_skymap_hits(fltr.database, gw, minmjd, maxmjd, verbose)
        nhits = len(skymaphits['diaObjectId'])
        if nhits > 0:
            skymaps.insert_skymap_hits(fltr.database, gw, skymaphits, verbose)
        totalnhits += nhits

    return totalnhits

if __name__ == "__main__":
    class mockFilter:
        def __init__(self):
            self.log = lasairLogging.getLogger("filter")
            self.database = db_connect.local()

    lasairLogging.basicConfig(stream=sys.stdout)
    from docopt import docopt
    args = docopt(__doc__)

    if args['--maxmjd']: maxmjd = float(args['--maxmjd'])
    else:                maxmjd = skymaps.mjdnow()

    if args['--minmjd']: minmjd = float(args['--minmjd'])
    else:                minmjd = maxmjd - settings.GW_ACTIVE_DAYS

    fltr = mockFilter()
    nhits = mmagw(fltr, minmjd=None, maxmjd=None, verbose=True)
    print('Found %s skymap hits' % str(nhits))
