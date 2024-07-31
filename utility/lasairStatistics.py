""" lasairStatistics
    Print out the lasair_statistics table for given nid, default today
"""
import sys
sys.path.append('../common')
from src import date_nid
from src.manage_status import manage_status

def printLasairStatistics(nid):
    print('Statistics for nid=%d' % nid)
    ms = manage_status()
    status = ms.read(nid)
    keys = sorted(status.keys())
    for key in keys:
        v = '%.3f' % status[key]
        print('%20s %20s' % (key, v.rjust(20)))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        nid = int(sys.argv[1])
    else:
        nid = date_nid.nid_now()
    printLasairStatistics(nid)

