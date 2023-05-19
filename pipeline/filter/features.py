""" Computes features of the light curve and builds and object record
"""
from __future__ import print_function
import json
import sys
import math
import numpy as np

def create_lasair_features(alert):
    taimax = 0.0
    taimin = 1000000000.
    for diaSource in alert['diaSourceList']:
        tai = diaSource['midPointTai']
        if tai > taimax: 
            taimax = tai
        if tai < taimin: 
            taimin = tai

    ncand = 0
    ncand_7 = 0
    for diaSource in alert['diaSourceList']:
        tai = diaSource['midPointTai']
        ncand += 1
        if taimax-tai < 7.0: 
            ncand_7 += 1

    # dictionary of attributes
    sets = {
        'taimax' : taimax,
        'taimin' : taimin,
        'ncand'  : ncand,
        'ncand_7': ncand_7
    }
    return sets
