""" How to look at the results of running a feature computation
    on a given alert.
"""
import sys
import json
sys.path.append('../../../../pipeline/filter')
sys.path.append('../../../../common/schema/lasair_schema')
from objects import schema as objectSchema
from features import fastfinder

if __name__ == "__main__":
    with open("sample_alerts/lsst1.json") as lsst1:
        alert = json.load(lsst1)
        f = fastfinder.fastfinder(alert)
        ret = f.run()
        for k,v in ret.items():
            print('%s --> %f' % (k, v))

