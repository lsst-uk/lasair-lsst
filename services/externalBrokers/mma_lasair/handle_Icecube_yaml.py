"""
Reads the yaml file for namespace Icecube
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
        'far'   : data['ALERT']['FAR'],
        'energy': data['ALERT']['ENERGY'],
        'signal': data['ALERT']['SIGNAL'],
    }
    # Should be a sky point near the most likely part of the skymap
    #radec = data['EXTRA']['central coordinate']['equatorial'].split()
    radec = '0.0 0.0'.split()
    loc = {
        'RA'      :data['ALERT']['RA'],
        'Dec'     :data['ALERT']['DEC'],
        }
    params['location'] = loc

    # Event time as MJD and as UT
    event_tai  = data['HEADER']['MJD-OBS']

    # decide if we want it
    # If this function returns a string, it is a reason why the event was rejected
    # Keep the BNS and NSBH, only keep BBH if small area
    # First find the most likely classification

    return {
        'event_tai':event_tai, 
        'loc': loc,
        'more_info': 'This is a high energy neutrino event from Icecube',
        'params':params,
    }
