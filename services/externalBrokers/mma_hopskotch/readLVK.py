import logging
import os, sys
import yaml
import json
from io import BytesIO
import numpy as np   
from copy import deepcopy
from astropy.table import Table
from astropy import units as u
import math

def uniq2order(uniq):
    """
    Convert HEALPix NUNIQ index to HEALPix order.
    """
    uniq = np.asarray(uniq, dtype=np.int64)

    return (np.floor(np.log2(uniq)).astype(int) // 2) - 1


def uniq2pixarea(uniq):
    """
    Return area of HEALPix NUNIQ pixels in steradians.
    """
    order = uniq2order(uniq)

    nside = 1 << order
    npix = 12 * nside * nside

    return 4.0 * np.pi / npix

def handleDataDict(dataDict, options, logger):
    # where the output goes
    dir = options['--directory']

    # used to throttle the numbers
    superEventId = dataDict['superevent_id']
    eventType = superEventId[0] # M, T or S

    alertTimeStamp = dataDict['time_created'].replace(' ','T').replace('Z','').replace(':','').replace('-','')
    alertType = dataDict['alert_type'].lower()
    alertName = superEventId + '_' + alertTimeStamp + '_' + alertType
    alertDir = alertName.replace('_','/',1)
    msg = "Alert Received: %s" % alertName
    if logger: logger.info(msg)
    else:      print(msg)

    # Act on all events unless we only want superevents. Need to think about the logic!
    if eventType != 'S' and options['--superevents']:
        msg= "Skipping over this event."
        if logger: logger.info(msg)
        else:      print(msg)
        return None

    # Write the event meta into the databases
    if dataDict['event'] is not None:
        meta = writeMeta(options, dataDict, logger)
        if meta:
            for k,v in meta.items():
                msg= "%s = %s" % (k, str(v))
                if logger: logger.info(msg)
                else:      print(msg)
            # Overwrite the superevent info every time a new update arrives.
            os.makedirs(dir + '/' + alertDir, exist_ok = True)
            with open(dir + '/' + alertDir + '/meta.yaml', 'w') as yamlFile:
                yamlFile.write(yaml.dump(meta))

    # write the skymap
    if dataDict['event'] is not None:
        skymap = dataDict['event']['skymap']
        os.makedirs(dir + '/' + alertDir, exist_ok = True)
        with open(dir + '/' + alertDir + '/map.fits', 'wb') as fitsFile:
            fitsFile.write(skymap)

    # make the MOCs
    contours = options.get('--contours', '90')
    if dataDict['event'] is not None:
        for contour in contours.split(','):
            skymap = dataDict['event']['skymap']
            try:
                c = float(contour)/100.0
                os.makedirs(dir + '/' + alertDir, exist_ok = True)
                writeMOC(BytesIO(skymap), dir + '/' + alertDir + '/' + contour + '.moc', c, logger)
            except ValueError as e:
                msg= "Contour %s is not a float" % contour
                if logger: logger.error(msg)
                else:      print(msg)
    return "success"

def getContourArea(inputFilePointer, contour, logger):
    # this could be replaced by 
    # ALL_SKY = 180*180*4/math.pi
    # area =  moc.sky_fraction * ALL_SKY

    # Read and verify the input
    skymap = Table.read(inputFilePointer, format='fits')

    # Sort by prob density of pixel
    skymap.sort('PROBDENSITY', reverse=True)

    # Get area*probdensity for each pixel
    pixel_area = uniq2pixarea(skymap['UNIQ'])

    # Probability per pixel
    prob = pixel_area*skymap['PROBDENSITY']
    cumprob = np.cumsum(prob)

    # Should be 1.0. But need not be.
    sumprob = np.sum(prob)

    # Find the index where contour of prob is inside
    i = cumprob.searchsorted(contour*sumprob)
    area = float(pixel_area[:i].sum() * (180/math.pi)**2)

    return area


def writeMOC(inputFilePointer, outputMOCName, contour, logger):
    """writeMOC.

    Args:
        inputFilePointer:
        outputMOCName:
        contour:
        logger:
    """
    from astropy.table import Table
    from astropy.io import fits
    from astropy import units as u
    import numpy as np
    import math
    #from ligo.skymap.moc import uniq2pixarea

    # Read and verify the input
    skymap = Table.read(inputFilePointer, format='fits')
    #print('Input multi-order skymap:')
    #logger.info(skymap.info)

    # Sort by prob density of pixel
    skymap.sort('PROBDENSITY', reverse=True)

    # Get area*probdensity for each pixel
    pixel_area = uniq2pixarea(skymap['UNIQ'])
    #print('Total area = %.1f\n' % (np.sum(pixel_area) * (180/math.pi)**2))

    # Probability per pixel
    prob = pixel_area*skymap['PROBDENSITY']
    cumprob = np.cumsum(prob)

    # Should be 1.0. But need not be.
    sumprob = np.sum(prob)
    #logger.info('Sum probability = %.3f\n' % sumprob)

    # Find the index where contour of prob is inside
    i = cumprob.searchsorted(contour*sumprob)
    area_wanted = pixel_area[:i].sum()
    #logger.info('Area of %.2f contour is %.2f sq deg' % \
    #   (contour, area_wanted * (180/math.pi)**2))

    # A MOC is just an astropy Table with one column of healpix indexes
    skymap = skymap[:i]
    skymap = skymap['UNIQ',]
    #logger.info(skymap.info)
    skymap.write(outputMOCName, format='fits', overwrite=True)
    # 2023-09-21 KWS There's a bug in MOCpy that requires format to be '1K'
    #                rather than the default 'K' (which is perfectly valid).
    h = fits.open(outputMOCName)
    header = h[1].header
    header['TFORM1'] = '1K'
    h.writeto(outputMOCName, overwrite=True)
    h.close()

    msg = 'MOC file %s written' % outputMOCName
    if logger: logger.info(msg)
    else:      print(msg)

def writeMeta(options, dataDict, logger):
    #import MySQLdb
    from astropy.io import fits

    mjd = None
    distance = None
    distanceStd = None
    creator = None
    eventMeta = {}

    dataDictCopy = deepcopy(dataDict)
    skymap = dataDictCopy['event']['skymap']

    areas = {}
    contours = options.get('--contours', '90')
    for c in contours.split(','):
        areas['area' + str(c)] = round(getContourArea(BytesIO(skymap), float(c)/100.0, logger), 3)

    # Some info (e.g. distance) only in the FITS file
    h = fits.open(BytesIO(skymap))
    header = h[1].header

    try:
        mjd = header['MJD-OBS']
    except KeyError as e:
        msg = "The MJD-OBS variable is missing."
        if logger: logger.error(msg)
        else:      print(msg)

    try:
        distance = header['DISTMEAN']
    except KeyError as e:
        msg = "The DISTMEAN variable is missing."
        if logger: logger.error(msg)
        else:      print(msg)

    try:
        distanceStd = header['DISTSTD']
    except KeyError as e:
        msg = "The DISTSTD variable is missing."
        if logger: logger.error(msg)
        else:      print(msg)

    try:
        creator = header['CREATOR']
    except KeyError as e:
        msg = "The CREATOR variable is missing."
        if logger: logger.error(msg)
        else:      print(msg)

    # Remove the skymap from the dictionary.
    try:
        dataDictCopy['event'].pop('skymap')
    except KeyError as e:
        pass

    try:
        dataDictCopy.pop('external_coinc')
    except KeyError as e:
        pass

    eventMeta = {'ALERT': dataDictCopy,
                 'EXTRA': areas,
                 'HEADER': {'MJD-OBS': mjd,
                            'DISTMEAN': distance,
                            'DISTSTD': distanceStd,
                            'CREATOR': creator}}

    return eventMeta

if __name__=="__main__":
    dataDict = json.loads(open('sample_input/igwn.json').read())
    skymap = open('sample_input/igwn_skymap.fits', 'rb').read()
    dataDict['event']['skymap'] = skymap
    options = {
        '--superevents': False,
        '--directory'  : 'sample_output/LVK',
        '--contours'   : '10,50,90',
    }
    ret = handleDataDict(dataDict, options, logger=None)
    print(ret)
