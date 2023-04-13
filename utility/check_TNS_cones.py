import sys
sys.path.append('../common')
import settings
import json
from src import db_connect
from subprocess import Popen, PIPE

msl = db_connect.remote()

cursor = msl.cursor(buffered=True, dictionary=True)
query = 'SELECT tns_name FROM crossmatch_tns WHERE tns_name NOT IN '
query += '(SELECT name FROM watchlist_cones WHERE wl_id=%d)' % settings.TNS_WATCHLIST_ID

cursor.execute(query)
n = 0
for row in cursor:
    print(row['tns_name'])
    n += 1

assert(n==0)
print('Every crossmatch_tns is in watchlist_cones')
