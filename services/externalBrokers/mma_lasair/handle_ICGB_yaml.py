"""
Reads the yaml file for namespace ICC
"""
import os, sys
import json
import time

from datetime import datetime, timedelta

sys.path.append('../../../common')
import settings

def handle(data):
    params = {
        'far'   : data['ALERT']['far'],
        'energy': data['ALERT']['nu_energy'],
        'signal': data['ALERT']['p_astro'],
    }
    # Should be a sky point near the most likely part of the skymap
    #radec = data['EXTRA']['central coordinate']['equatorial'].split()
    radec = '0.0 0.0'.split()
    loc = {
        'RA'      :data['ALERT']['ra'],
        'Dec'     :data['ALERT']['dec'],
        }
    params['location'] = loc

    # Event time as MJD and as UT
    event_tai  = data['HEADER']['MJD-OBS']

    # decide if we want it

    return {
        'event_tai':event_tai, 
        'loc': loc,
        'more_info': 'This is a high energy neutrino event from Icecube GoldBronze',
        'params':params,
    }
