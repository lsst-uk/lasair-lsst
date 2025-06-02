# This code transfers a table from the local database to the main database
# First it gets the attributes from the main database in order
# Then is makes tghe CSV file, and transfers it over

import os, subprocess, tempfile
import settings
cmdremote = 'mysql --user=%s --database=ztf --password=%s --host=%s '
cmdremote = cmdremote % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_HOST)

cmdlocal =  'mysql --user=%s --database=ztf --password=%s '
cmdlocal = cmdlocal % (settings.LOCAL_DB_USER, settings.LOCAL_DB_PASS)

def fetch_attrs(table_name):
    # fetch the attributes from the main database in correct order
    fetch_attrs = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s' "
    fetch_attrs = fetch_attrs % table_name
    with tempfile.NamedTemporaryFile(delete_on_close=False) as in_memory_file:
        in_memory_file.write(fetch_attrs.encode('utf8'))
        in_memory_file.close()
        cmd = cmdremote + '<' + in_memory_file.name
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out = result.stdout.read().decode('utf-8')
        attrs = out.split('\n')[1:-1]
    return attrs

def transfer_csv(table_name, attrs):
    # delete the old file (might be done elsewhere)
    #os.system('sudo --non-interactive rm /data/mysql/%s.txt' % table_name)

    # make the CSV file in the order wanted by the main database
    make_csv = 'SELECT '
    make_csv += ','.join(attrs)
    make_csv += " FROM things INTO OUTFILE '/data/mysql/%s.txt' " % table_name
    make_csv += "FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n'"
    with tempfile.NamedTemporaryFile(delete_on_close=False) as in_memory_file:
        in_memory_file.write(make_csv.encode('utf8'))
        in_memory_file.close()
        cmd = cmdlocal + '<' + in_memory_file.name
        os.system(cmd)
    
    # push the CSV to the main database
    push_csv = "LOAD DATA LOCAL INFILE '/data/mysql/%s.txt' " % table_name
    push_csv += "REPLACE INTO TABLE %s " % table_name
    push_csv += "FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n'"
    with tempfile.NamedTemporaryFile(delete_on_close=False) as in_memory_file:
        in_memory_file.write(push_csv.encode('utf8'))
        in_memory_file.close()
        cmd = cmdremote + '<' + in_memory_file.name
        os.system(cmd)

if __name__ == '__main__':
    table_name = 'things'
    attrs = fetch_attrs(table_name)
    transfer_csv(table_name, attrs)
