"""
Rebuilds features for Lasair. Takes a set of files, with an objectId on each line of each file.
within the list of objects,
and makes CSV files suitable for ingestion with sister program csv_to_database.
Can run with multiprocessing.
Usage:
    runner.py (--in=IN) (--files=file_list) (--out=OUT)

Options:
  --in=IN            Directory name for input files
  --files=file_list  Files to be processed, one per process
  --out=OUT          Directory name for output
"""
import sys, time, json
sys.path.append('../../../common')
import settings
from src import db_connect
from docopt import docopt
from multiprocessing import Process, Manager
from build import get_cassandra_session, get_mysql_attrs, rebuild_features

def run(runargs):
    global cassandra_session, schema_names
    indir    = runargs['--in']
    filename = runargs['--filename']
    outdir   = runargs['--out']

    print('filename ', filename)
    
    cassandra_session = get_cassandra_session()
    msl = db_connect.readonly()
    schema_names = get_mysql_attrs(msl)

    t = time.time()
    nobject = 0
    objectList = []
    for row in open(indir + '/' + filename).readlines():
        objectList.append(row.strip())
    nobject = len(objectList)

    ndone = 0
    csvlines = ''
    for objectId in objectList:
        csvline = rebuild_features({
           'objectId': objectId,
           'schema_names': schema_names,
           'cassandra_session':cassandra_session,
        })
        if csvline:
            csvlines += csvline + '\n'
        ndone += 1
        #print(ndone, ' of ', nobject)

    f = open('%s/%s.csv' % (outdir, filename) , 'w')
    f.write(csvlines)
    f.close()

    if nobject ==  0:
        print('no objects found')
        sys.exit(1)

    t = time.time() - t
    print('%s: %d objects in %.1f msec each' % (filename, nobject, t*1000.0/nobject))

    cassandra_session.shutdown()

if __name__ == "__main__":
    args = docopt(__doc__)
    files = args['--files'].split(',')
    nprocess = len(files)
    print('Running %d processes' % nprocess)

    process_list = []
    for iprocess in range(nprocess):
        runargs = args.copy()
        runargs['--filename'] = files[iprocess]
        p = Process(target=run, args=(runargs,))
        process_list.append(p)
        p.start()

    for p in process_list:
        p.join()
