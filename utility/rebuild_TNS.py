"""
Utility to completely rebuild the TSBN is Lasair, including 3 tables;
crossmatch_tns
watchlist_cones
watchlist_hits
"""
import sys, time

sys.path.append('../common')
import settings
from src import db_connect, date_nid
import src.run_crossmatch_optimised as run_crossmatch

sys.path.append('../services/externalBrokers/TNS')
from poll_tns import getTNSData, countTNSRow

if __name__ == "__main__":
    conn = db_connect.remote()

    # Fetch all the TNS records for the central place
    # insert into crossmatch_tns table
    # build the watchlist_cones table
    t0 = time.time()
    options = {'daysAgo': 'All', 'radius':False}
    getTNSData(options, conn)
    print('Time to fetch TNS = %.0f seconds' % (time.time()-t0))

    # count them up
    countTNS = countTNSRow(conn)
    print('Total number in TNS = ', countTNS)

    # crossmatch with all Lasair objects
    # build the watchlist_hits table
    t0 = time.time()
    radius = 3 # arcseconds
    hits, message = run_crossmatch.run_crossmatch(\
            None, radius, settings.TNS_WATCHLIST_ID)
    print('Time to crossmatch = %.0f seconds' % (time.time()-t0))

    conn.commit()
    conn.close()
