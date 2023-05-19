""" Computes features of the light curve and builds and object record
"""
from __future__ import print_function
import json, sys, time
import numpy as np

def float_copyer(alert=None):
    """ Copy the float/double attributes from daiObject """
    copy_float_attr = [
        "ra", "decl", "radecTai",
        "uPSFluxMean", "gPSFluxMean", "rPSFluxMean", "iPSFluxMean", "zPSFluxMean", "yPSFluxMean",
    ]
    dict = {}
    for attr in copy_float_attr:
        if alert:
            dict[attr] = alert['diaObject'][attr]
        else:
            dict[attr] = 0.0
    return dict

def minMaxTai(alert=None):
    """Min and max time of the diaSources """

    if not alert:
        return {
            "taimin": 0.0,
            "taimax": 0.0,
        }

    taiList = [diaSource['midPointTai'] for diaSource in alert['diaSourceList']]
    return {
        "taimin": min(taiList),
        "taimax": max(taiList),
    }


def mjd_now():
    """ *return the current UTC time as an MJD* """
    return time.time() / 86400 + 40587.0

def ncand(alert=None):
    """Number of diaSources -- all and last 7 days """
    if not alert:
        return {
            "ncand": 0,
            "ncand_7": 0,
        }
  
    taiList = [diaSource['midPointTai'] for diaSource in alert['diaSourceList']]
    taiNow = mjd_now()
    ncand_7 = 0
    for tai in taiList:
        if tai > taiNow -7:
            ncand_7 += 1
    return {
        "ncand": len(taiList), 
        "ncand_7": ncand_7,
    }

builder_functions = [
    float_copyer,
    minMaxTai,
    ncand,
]

def create_lasair_features(alert):
    sets = {}
    for bf in builder_functions:
        result = bf(alert)
        sets = {**sets, **result}
    return sets

##############
if __name__ == '__main__':
    alert = json.loads(open('../../utility/features/BazinBB/1000.json').read())
    sets = create_lasair_features(alert)
    print(sets)
