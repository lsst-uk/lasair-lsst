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

# Makes a MOC from a single-level (Icecube) type healpix file
def moc_single_level(contour, input_file, output_file, logger):
    map_data, header = hp.read_map(input_file, h=True, dtype=None)
    header_dict = dict(header)
    
    # Determine grid properties
    nside = hp.npix2nside(len(map_data))
    order = hp.nside2order(nside)
    ordering = header_dict.get('ORDERING', 'RING').strip().upper()
    
    msg = f"moc_single_level: NSIDE = {nside} (Order {order}), Ordering = {ordering}"
    if logger: logger.info(msg)
    else:      print(msg)

    prob = map_data / map_data.sum()
    order_idx = np.argsort(prob)[::-1]
    cum = np.cumsum(prob[order_idx])

    credible = np.empty_like(prob)
    credible[order_idx] = cum
    top_pixels = np.where(credible <= contour / 100.0)[0]
    
    if ordering == 'RING':
        nested_pixels = hp.ring2nest(nside, top_pixels)
    else:
        nested_pixels = top_pixels
    
    moc = MOC.from_healpix_cells(
        ipix=nested_pixels,
        depth=order,
        max_depth=order
    )
    moc.save(output_file, format='fits', overwrite=True)
    ALL_SKY = 180*180*4/math.pi
    area =  moc.sky_fraction * ALL_SKY
    msg = f"moc_single_level: area {area} saved to {output_file}"
    if logger: logger.info(msg)
    else:      print(msg)

    return area

if __name__=="__main__":
    dataDict = json.loads(open('sample_input/icecube.json').read())
    options = {
        '--superevents': False,
        '--directory'  : 'sample_output/icecube',
        '--contours'   : '10,50,90',
    }
    ret = handleDataDict(dataDict, options, logger=None)
    print(ret)
