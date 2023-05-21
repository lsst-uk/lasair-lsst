""" Clear out the local database
"""
import sys
sys.path.append('../../common')
from src import db_connect
import settings

try:
    msl = db_connect.local()
    cursor = msl.cursor(buffered=True, dictionary=True)
except:
    print('ERROR in filter/refresh: cannot clear local database')
    sys.stdout.flush()

query = 'TRUNCATE TABLE objects'
cursor.execute(query)

query = 'TRUNCATE TABLE sherlock_classifications'
cursor.execute(query)

query = 'TRUNCATE TABLE watchlist_hits'
cursor.execute(query)

query = 'TRUNCATE TABLE area_hits'
cursor.execute(query)

