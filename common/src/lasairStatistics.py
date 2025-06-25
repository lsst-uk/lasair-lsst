""" lasairStatistics
    Print out the lasair_statistics table for given nid, default today
"""
import sys
try:
    from . import date_nid
    from . import db_connect
    from .manage_status import manage_status
except:
    import date_nid
    import db_connect
    from manage_status import manage_status

def combine_status(status):
    # the keys come in as apple_0=123, apple_1=199 etc from the nodes
    # here we combine them into a list apple = [123,199]
    keys = sorted(status.keys())
    new_status = {}
    for key in keys:
        if not key in status:
            continue
        v = '%.0f' % status[key]
        # collect values from different nodes
        if key.endswith('_0'):
            kl = []
            root = key[:-2]
            for i in range(10):
                other_key = '%s_%d' % (root, i)
                if other_key in status:
                    s = int(round(status[other_key], 0))
                    kl.append(s)
                    del status[other_key]
                else:
                    new_status[root] = str(kl)
                    break
        else:
            s = int(round(status[key], 0))
            new_status[key] = str(s)
    return new_status

def printLasairStatistics(nid):
    print('Statistics for nid=%d' % nid)
    ms = manage_status()
    status = ms.read(nid)
    new_status = combine_status(status)
    for k,v in new_status.items():
        print('%20s %20s' % (k, v.ljust(20)))

def delete_nid(nid):
    print('Statistics for nid=%d' % nid)
    ms = manage_status()
    ms.delete(nid)
    print('Statistics deleted for nid=', nid)
    
if __name__ == '__main__':
    if len(sys.argv) > 1: 
        nid = int(sys.argv[1])
        if len(sys.argv) > 2 and sys.argv[2].strip() == 'delete':
            delete_nid(nid)
    else:
        nid = date_nid.nid_now()

    printLasairStatistics(nid)

