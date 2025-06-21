# This code transfers a table from the local database to the main database
# First it gets the attributes from the main database in order
# Then is makes tghe CSV file, and transfers it over

def fetch_attrs(msl_remote, table_name, log=None):
    # fetch the attributes from the main database in correct order
    fetch_attrs = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s' "
    fetch_attrs = fetch_attrs % table_name
    cursor = msl_remote.cursor(buffered=True, dictionary=True)
    try:
        cursor.execute(fetch_attrs)
    except Exception as e:
        if log: log.error('Fetch attrs failed:' + str(e))
        return False
    attrs = []
    for row in cursor:
        cn = row['column_name']
        if not cn in attrs:
            attrs.append(cn)
    cursor.close()
    return attrs

def transfer_csv(msl_local, msl_remote, attrs, table_from, table_to, log=None):
    # delete the old file (might be done elsewhere)
    #os.system('sudo --non-interactive rm /data/mysql/%s.txt' % table_name)

    # make the CSV file in the order wanted by the main database
    cursor_local = msl_local.cursor(buffered=True, dictionary=True)
    make_csv = 'SELECT '
    make_csv += ','.join(attrs)
    make_csv += " FROM %s INTO OUTFILE '/data/mysql/%s.txt' " % (table_from, table_from)
    make_csv += "FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n'"
    try:
        cursor_local.execute(make_csv)
    except Exception as e:
        if log: log.error('Fetch attrs failed:' + str(e))
        return False
    
    # push the CSV to the main database
    cursor_remote = msl_remote.cursor(buffered=True, dictionary=True)
    push_csv = "LOAD DATA LOCAL INFILE '/data/mysql/%s.txt' " % table_from
    push_csv += "REPLACE INTO TABLE %s " % table_to
    push_csv += "FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n'"
    cursor_remote.execute(push_csv)
    msl_remote.commit()
    return True

if __name__ == "__main__":
    import os, sys
    sys.path.append('../../common')
    sys.path.append('../../common/src')
    import db_connect
    msl_local = db_connect.local()
    msl_remote = db_connect.remote(allow_infile=True)

    attrs = fetch_attrs(msl_remote, 'objects')
    print(len(attrs), 'attributes')

    os.system('sudo --non-interactive rm /data/mysql/*.txt')

    transfer_csv(msl_local, msl_remote, attrs, 'objects', 'objects')
