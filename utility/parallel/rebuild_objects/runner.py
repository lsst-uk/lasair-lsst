"""
Rebuilds features for Lasair. Takes a start OFFSET, end OFFSET,
within the list of objects,
and makes CSV files suitable for ingestion with sister program csv_to_database.
Can run with multiprocessing.
Usage:
    runner.py [--nprocess=NP] (--soff=SOFF) (--eoff=EOFF) (--out=OUT)

Options:
  --nprocess=NP  Number of processes to use [default: 1]
  --soff=SOFF    Start OFF, example 1000000
  --eoff=EOFF    End OFF,   example 1000010
  --out=OUT      Directory name for output
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
    nprocess = int(runargs['--nprocess'])
    iprocess = int(runargs['--iprocess'])

    global_soff = int(runargs['--soff'])
    global_eoff = int(runargs['--eoff'])
    out = runargs['--out']
    job = runargs['--job']

    per_process = (global_eoff - global_soff)/nprocess
    soff = global_soff + per_process*iprocess
    if iprocess == nprocess-1:
        eoff = global_eoff
    else:
        eoff = global_soff + per_process*(iprocess+1)

    print('%d: start OFF %d end OFF %d' % (iprocess, soff, eoff))
    
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    
    query = "SELECT objects.objectId FROM objects "
    query += "LIMIT %d OFFSET %d" % (eoff-soff, soff)
    cursor.execute(query)

    cassandra_session = get_cassandra_session()
    schema_names = get_mysql_attrs(msl)

    t = time.time()
    nobject = 0
    objectList = []
    for row in cursor:
        objectList.append(row['objectId'])
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

    f = open('%s/%s_%s.csv' % (out, job, iprocess) , 'w')
    f.write(csvlines)
    f.close()

    if nobject ==  0:
        print('no objects found')
        sys.exit(1)

    t = time.time() - t
    print('%d: %d objects in %.1f msec each' % (iprocess, nobject, t*1000.0/nobject))

    cassandra_session.shutdown()

if __name__ == "__main__":
    args = docopt(__doc__)
    nprocess = int(args['--nprocess'])
    print('Running %d processes' % nprocess)
    global_soff = int(args['--soff'])
    global_eoff = int(args['--eoff'])
    job = '%07d_%07d' % (global_soff, global_eoff)

    process_list = []
    for iprocess in range(nprocess):
        runargs = args.copy()
        runargs['--iprocess'] = iprocess
        runargs['--job'] = job
        p = Process(target=run, args=(runargs,))
        process_list.append(p)
        p.start()

    for p in process_list:
        p.join()
    print(job, 'Finished')
