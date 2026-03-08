""" annotationStatistics
    Print out the statistics for complex annotators
"""
import sys
sys.path.append('../common')
from src import date_nid
import src.db_connect as db_connect

def annotations_in(cursor, ann_name):
    # How many annotations contributed by this annotator, for the last 7 days
    query = "SELECT count(*) AS nann, DATE(timestamp) as date FROM annotations "
    query += "WHERE topic='%s' AND timestamp > DATE(NOW() - INTERVAL 7 DAY) "
    query += "GROUP BY DAY(timestamp), MONTH(timestamp), YEAR(timestamp)"
    query = query % ann_name
    cursor.execute(query)
    print('\n** Annotations ingested for %s' % ann_name)
    print(' date    number')
    for row in cursor:
        print('%s %8d' % (row['date'], row['nann']))

    query = f'SELECT active FROM annotators WHERE topic="{ann_name}"'
    cursor.execute(query)
    for row in cursor:
        return row['active']

def fast_filters(cursor, ann_name):
    # List of active filters that are immediately run as a result of the fast annotator
    query = " SELECT last_name, active, name FROM myqueries JOIN auth_user ON user=id "
    query += "WHERE tables LIKE '%%%s%%' and active > 0 ORDER BY last_name"
    query = query % ann_name
    cursor.execute(query)
    print('\n** Fast annotation filters resulting from %s' % ann_name)
    print('   Last name  active  Filter name')
    for row in cursor:
        print('%15s %d %s' % (row['last_name'], row['active'], row['name']))

def bytes_out(cursor, filter_name):
    # How many bytes output on public Kafka by this filter, for the last 7 days
    nid = date_nid.nid_now()
    query = 'SELECT name,value,nid FROM lasair_statistics WHERE nid>%d AND name LIKE "%%%s_bytes%%"'
    query = query % (nid-7, filter_name)
    cursor.execute(query)
    print('\n** Bytes out by Kafka to  %s' % filter_name)
    print(' date    Mbytes')
    for row in cursor:
        date = date_nid.nid_to_date(row['nid'])
        bytes = f'{int(row["value"]):,}'
        print('%s %20s' % (date, bytes))

if __name__ == "__main__":
    import os, sys
    feeder_name = None
    if len(sys.argv) > 1:
        ann_name    = sys.argv[1]
    if len(sys.argv) > 2:
        feeder_name = sys.argv[2]
    if len(sys.argv) == 1:
        print('Usage: python3 annotationStatistics.py <annotation_name> <feeder_name>')
        print('examples:')
        print('  python3 annotationStatistics.py r0b_lvra lvra_fodder')
        print('  python3 annotationStatistics.py NEEDLE_LSST needle_input_filter_test')
        sys.exit()

    msl = db_connect.remote()
    cursor  = msl.cursor(buffered=True, dictionary=True)

    active = annotations_in(cursor, ann_name)
    if active  == 1:
        print('\nNORMAL ANNOTATOR')
    else:
        print('\nFAST ANNOTATOR')
        fast_filters  (cursor, ann_name)

    if feeder_name:
        bytes_out     (cursor, feeder_name)

