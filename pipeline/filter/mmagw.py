"""
mmagw.py
This code checks a batch of alerts against the active GW alerts.
"""
import os, sys
sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import db_connect, skymaps


def mmagw(fltr):
    maxmjd = skymaps.mjdnow()
    minmjd = maxmjd - 21 # three weeks
    main_database = db_connect.remote()

    try:
        skymaplist = skymaps.fetch_skymaps_by_mjd(main_database, minmjd, maxmjd)
    except Exception as e:
        fltr.log.error("ERROR in mmagw/mmagw" + str(e))
        return None

    for gw in skymaplist:
        skymaphits = skymaps.get_skymap_hits(fltr.database, gw, minmjd, maxmjd)
        if len(skymaphits['diaObjectId']) > 0:
            skymaps.insert_skymap_hits(fltr.database, gw, skymaphits)
