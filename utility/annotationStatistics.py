""" annotationStatistics
    Print out the statistics for the lvra system
"""
import sys
sys.path.append('../common')
from src import date_nid
import src.db_connect as db_connect

def bytes_out(cursor, query_name):
    nid = date_nid.nid_now()
    query = 'SELECT name,value,nid FROM lasair_statistics WHERE nid>%d AND name LIKE "%%%s_bytes%%"'
    query = query % (nid-7, query_name)
    cursor.execute(query)
    print('** Megabytes in %s' % query_name)
    print(' date    Mbytes')
    for row in cursor:
        print('%s %10.0f' % (date_nid.nid_to_date(row['nid']), (row['value']/1000000)))

def annotations_in(cursor, ann_name):
    query = "SELECT count(*) AS nann, DATE(timestamp) as date FROM annotations "
    query += "WHERE topic='%s' AND timestamp > DATE(NOW() - INTERVAL 7 DAY) "
    query += "GROUP BY DAY(timestamp), MONTH(timestamp), YEAR(timestamp)"
    query = query % ann_name
    cursor.execute(query)
    print('\n** Annotations in %s' % ann_name)
    print(' date    number')
    for row in cursor:
        print('%s %8d' % (row['date'], row['nann']))

def fast_filters(cursor, ann_name):
    query = " SELECT last_name, active, name FROM myqueries JOIN auth_user ON user=id "
    query += "WHERE tables LIKE '%%%s%%' and active > 0 ORDER BY last_name"
    query = query % ann_name
    cursor.execute(query)
    print('\n** Fast annotation filters from %s' % ann_name)
    print('   Last name  active  Filter name')
    for row in cursor:
        print('%15s %d %s' % (row['last_name'], row['active'], row['name']))

if __name__ == "__main__":
    msl = db_connect.remote()
    cursor  = msl.cursor(buffered=True, dictionary=True)
    bytes_out     (cursor, 'lvra-fodder')
    annotations_in(cursor, 'r0b_lvra')
    fast_filters  (cursor, 'r0b_lvra')

