import logging
import math
import os, sys
import yaml
import json
from io import BytesIO
import numpy as np   
from astropy.io import fits
import healpy as hp
from mocpy import MOC
import requests
from moc import moc_single_level

# Handling Icecube CASCADE events

def handleDataDict(dataDict, options, logger):
    # where the output goes
    dir = options['--directory']

    # fetch the skymap from the given URL
    if 'skymap_fits_url' in dataDict:
        r = requests.get(dataDict['skymap_fits_url'])
        skymap = r.content
    else:
        msg = 'Icecube dataDict has no skymap_fits_url. Quitting'
        if logger: logger.error(msg)
        else:      print(msg)
        return None

    # Use the event name for the directory
    # event name looks like "IceCubeCascade-260801a" so just take the part with the date
    if 'event_name' in dataDict:
        alertDir = dataDict['event_name'][-7:] + '/final/'
    else:
        msg = 'Icecube dataDict has no event_name. Quitting'
        if logger: logger.error(msg)
        else:      print(msg)


    # write the fits file to the alert directory
    os.makedirs(dir + '/' + alertDir, exist_ok = True)
    skymapFile = dir + '/' + alertDir + '/map.fits'
    with open(skymapFile, 'wb') as fitsFile:
        fitsFile.write(skymap)

    # make the MOCs
    areas = {}
    contours = options.get('--contours', '10,50,90')
    for contour in contours.split(','):
        os.makedirs(dir + '/' + alertDir, exist_ok = True)
        output_file = dir + '/' + alertDir + '/' + contour + '.moc'
        area = moc_single_level(int(contour), skymapFile, output_file, logger)
        areas[f'area{contour}'] = round(area, 3)

    # Fetch all the metadata from the Skymap FITS file
    h = fits.open(BytesIO(skymap))
    header = h[1].header
    mjd = header['EVENTMJD']
    alertDict = {}
    alertDict['RA']         = header['RA']
    alertDict['DEC']        = header['DEC']
    alertDict['CIRC_ERR90'] = header['HIERARCH CIRC_ERR90']
    alertDict['CIRC_ERR50'] = header['HIERARCH CIRC_ERR50']
    alertDict['ENERGY']     = header['ENERGY']
    alertDict['FAR']        = header['FAR']
    alertDict['SIGNAL']     = header['SIGNAL']
    creator = 'Icecube Neutrino Observatory'

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
    dataDict = json.loads(open('sample_hopskotch_input/ICC.json').read())
    options = {
        '--superevents': False,
        '--directory'  : 'sample_hopskotch_output/ICC',
        '--contours'   : '10,50,90',
    }
    ret = handleDataDict(dataDict, options, logger=None)
    print(ret)
