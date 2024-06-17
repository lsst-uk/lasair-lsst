import os, sys, json, io, gzip
from cassandra.cluster import Cluster
from gkdbutils.ingesters.cassandra import executeLoad
from confluent_kafka import Producer
import settings

def insert_cassandra(obj, cassandra_session):
    """insert_casssandra.
    Creates an insert for cassandra
    a query for inserting it.

    Args:
        alert:
    """

    # if this is not set, then we are not doing cassandra
    if not cassandra_session:
        return None   # failure of batch

    executeLoad(cassandra_session, 'SSObjects', [obj['SSObject']])
    executeLoad(cassandra_session, 'MPCORBs', [obj['MPCORB']])

    # will be list of real detections, each has a non-null candid
    diaSourceList = obj['DiaSourceList']
    ssSourceList = obj['SSSourceList']

    if len(diaSourceList) > 0:
        executeLoad(cassandra_session, 'diaSources', diaSourceList)

    if len(ssSourceList) > 0:
        executeLoad(cassandra_session, 'ssSources', ssSourceList)

    return len(diaSourceList)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        datadir = sys.argv[1]
    else:
        print('Usage: json_to_cassandra.py <dataset>')
        sys.exit()

    cluster = Cluster(settings.CASSANDRA_HEAD)
    cassandra_session = cluster.connect()
    cassandra_session.set_keyspace('adler')

    n = 0
    objList = None
    print(datadir)
    for file in os.listdir(datadir):
        if not file.endswith('gz'): continue
        
        del objList
        fin = gzip.open(datadir +'/'+ file, 'r')
        json_bytes = fin.read()
        fin.close()

        json_str = json_bytes.decode('utf-8')
        del json_bytes
        objList = json.loads(json_str)          
        del json_str

        for obj in objList:
            # there will never be an alert with no detections
            if len(obj['DiaSourceList']) < 1: continue

            insert_cassandra(obj, cassandra_session)
            
            n +=1
            if n%100 == 0: 
                print(n)
    print('%d alerts pushed to cassandra ' % n)
