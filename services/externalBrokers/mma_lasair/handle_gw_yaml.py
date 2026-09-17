"""
Reads the yaml file for namespace LVK
"""
import os, sys
import json
import time

from datetime import datetime, timedelta

sys.path.append('../../../common')
import settings

def handle(data):
    # extract the classification (BNS, BBS etc) and far (false alarm rate)
    params = {
        'classification': data['ALERT']['event']['classification'],
        'far': data['ALERT']['event']['far'],
    }
    # Should be a sky point near the most likely part of the skymap
    #radec = data['EXTRA']['central coordinate']['equatorial'].split()
    radec = '0.0 0.0'.split()
    loc = {
        'RA'      :float(radec[0].strip()), 
        'Dec'     :float(radec[1].strip()), 
        'distmean':data['HEADER']['DISTMEAN'], 
        'diststd' :data['HEADER']['DISTSTD'],
        }
    params['location'] = loc

    # Event time as MJD and as UT
    event_tai  = data['HEADER']['MJD-OBS']

    # decide if we want it
    # If this function returns a string, it is a reason why the event was rejected
    # Keep the BNS and NSBH, only keep BBH if small area
    # First find the most likely classification
    percent = 0
    gwclass = ''
    for k,v in params['classification'].items():
        if v>percent:
            percent = v
            gwclass = k

    area90 = data['EXTRA']['area90']
    good = (gwclass == 'BNS' or gwclass == 'NSBH') and area90 < settings.GW_BBH_MAX_AREA
    if not good:
        message = 'Classification = %s and area90 = %s' % (gwclass, str(area90))

    # What kind of MMA event is this
    more_info = 'This is a gravitational wave event from LIGO-Virgo-Kagra'

    return {
        'event_tai':event_tai, 
        'loc': loc,
        'more_info':'Gravitational wave event from LIGO-Virgo-Kagra', 
        'params':params,
    }
