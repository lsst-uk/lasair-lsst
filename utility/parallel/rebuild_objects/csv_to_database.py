import os, sys, time
sys.path.append('../../../common')
from src import db_connect
import settings

def handle(filename):
    sql  = "LOAD DATA LOCAL INFILE '%s' " % filename
    sql += "REPLACE INTO TABLE objects FIELDS TERMINATED BY ',' "
    sql += "ENCLOSED BY '\"' LINES TERMINATED BY '\n'"

    sqlfile = 'tmp.sql'
    f = open(sqlfile, 'w')
    f.write(sql)
    f.close()

    cmd =  "mysql --user=%s --database=ztf --password=%s --host=%s --port=%s < tmp.sql" 
    cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_HOST, settings.DB_PORT)
    print(cmd)
    os.system(cmd)

################
csvdir = sys.argv[1]
print ('Database', settings.DB_HOST, settings.DB_PORT)

tstart = time.time()
filelist =  os.listdir(csvdir)
filelist.sort()
n = 0
for csvfile in os.listdir(csvdir):
    filename = '%s/%s' % (csvdir,csvfile)
    os.system('wc %s' % filename)
    t = time.time()
    handle(filename)
    n += 1
    print('%d: %s imported in %.1f seconds' % (n, csvfile, (time.time() - t)))
print('Finished in %.1f seconds' % (time.time() - tstart))

