import logging
import math
import os, sys
import yaml
import json
from datetime import datetime, timezone
import healpy as hp
import requests
from make_skymap import make_skymap
from moc import moc_single_level

# Handling Icecube GOLDBRONZE events

def datetime_to_mjd(s):
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))

    mjd_epoch = datetime(1858, 11, 17, tzinfo=timezone.utc)
    return (dt - mjd_epoch).total_seconds() / 86400.0

def handleDataDict(dataDict, options, logger):
    # where the output goes
    dir = options['--directory']

    skymap = make_skymap(dataDict['ra'], dataDict['dec'], dataDict['ra_dec_error'])

    # Use the event name for the directory
    # event name looks like "IceCubeCascade-260801a" so just take the part with the date
    if 'event_name' in dataDict:
        alertDir = dataDict['event_name'][0][-7:] + '/final/'
    else:
        msg = 'Icecube dataDict has no event_name. Quitting'
        if logger: logger.error(msg)
        else:      print(msg)


    # write the fits file to the alert directory
    os.makedirs(dir + '/' + alertDir, exist_ok = True)
    skymapFile = dir + '/' + alertDir + '/map.fits'
    hp.write_map(skymapFile, skymap, overwrite=True)

    # make the MOCs
    areas = {}
    contours = options.get('--contours', '10,50,90')
    for contour in contours.split(','):
        os.makedirs(dir + '/' + alertDir, exist_ok = True)
        output_file = dir + '/' + alertDir + '/' + contour + '.moc'
        area = moc_single_level(int(contour), skymapFile, output_file, logger)
        areas[f'area{contour}'] = round(area, 3)

    # Fetch all the metadata from the JSON file
    alertDict = {}
    alertDict['alert_datetime'] = dataDict['alert_datetime']
    mjd = datetime_to_mjd(dataDict['alert_datetime'])
    alertDict = {}
    alertDict['ra']           = dataDict['ra']
    alertDict['dec']          = dataDict['dec']
    alertDict['ra_dec_error'] = dataDict['ra_dec_error']
    alertDict['nu_energy']    = dataDict['nu_energy']
    alertDict['far']          = dataDict['far']
    alertDict['p_astro']      = dataDict['p_astro']
    creator = 'Icecube Neutrino Observatory Gold/Bronze'

    eventMeta = {'ALERT': alertDict,
                 'EXTRA': areas,
                 'HEADER': {'MJD-OBS': mjd,
                            'CREATOR': creator}}
    # Write the metadat as a yaml
    os.makedirs(dir + '/' + alertDir, exist_ok = True)
    with open(dir + '/' + alertDir + '/meta.yaml', 'w') as yamlFile:
        yamlFile.write(yaml.dump(eventMeta))
    return 'success'

if __name__=="__main__":
    indata = '../../../tests/unit/services/externalBrokers/sample_hopskotch_input/ICGB.json'
    outdir =  '../../../tests/unit/services/externalBrokers/sample_hopskotch_output/ICGB'
    dataDict = json.loads(open(indata).read())
    options = {
        '--superevents': False,
        '--directory'  : outdir,
        '--contours'   : '10,50,90',
    }

    ret = handleDataDict(dataDict, options, logger=None)
    print(ret)
