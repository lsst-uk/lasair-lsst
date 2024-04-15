"""
Checks the directory of GW alerts for those we haven't seen before
then tries to insert it into the database

Usage:
    readGW.py [--minmjd=minmjd]
              [--maxmjd=maxmjd]

Options:
    --minmjd=minmjd    Choose all skymaps older than this MJD
    --maxmjd=maxmjd    Choose all skymaps younger than this MJD
"""
import os, sys
import json
import io
import yaml
from yaml import CLoader as Loader
import base64
import traceback
import time
import numpy as np

from mocpy import MOC, WCS
import astropy.units as u
import astropy_healpix as ah
from astropy.table import QTable
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

sys.path.append('../../../common')
import settings
from src import db_connect, skymaps

def insert_gw_alert(database, dir, otherId, version):
    """ Deals with a given skymap
    """
    # open the meta.yaml file
    datadir = '%s/%s/%s' % (dir, otherId, version)
    f = open(datadir + '/meta.yaml')
    data = yaml.load(f, Loader=Loader)
    f.close()

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
    event_date = mjd2date(event_tai)

    # Areas of the 10%, 50%, and 90% contours in sq degrees
    area10 = data['EXTRA']['area10']
    area50 = data['EXTRA']['area50']
    area90 = data['EXTRA']['area90']

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

    if      gwclass != 'BNS' and \
            gwclass != 'NSBH' and \
            area90 > settings.GW_BBH_MAX_AREA:
        return 'Classification = %s and area90 = %s' % (gwclass, str(area90))

    # Deal with the 3 MOCs
    moc10 = read_moc(datadir, '10')
    moc50 = read_moc(datadir, '50')
    moc90 = read_moc(datadir, '90')
    mocimage = make_image(moc10, moc50, moc90)

    # get most probable point
    skymap_filename = datadir + '/map.fits'
    (raprob, deprob) = get_ra_dec(skymap_filename)
    loc['RA'] = raprob
    loc['Dec'] = deprob

    # What kind of MMA event is this
    namespace = 'LVK'
    more_info = 'This is a gravitational wave event from LIGO-Virgo-Kagra'

    # Insert into database
    query = """
    INSERT INTO mma_areas (
        event_tai, event_date, mocimage, 
        namespace, otherId, version, more_info,
        area10, area50, area90, params
    ) VALUES (
        %f, "%s", "%s",
        "%s", "%s", "%s","%s",
        %f, %f, %f, '%s'
    ) """

    query = query % ( \
        event_tai, event_date, bytes2string(mocimage),  \
        namespace, otherId, version, more_info, \
        area10, area50, area90, json.dumps(params) \
    )

    cursor = database.cursor(buffered=True, dictionary=True)
    cursor.execute (query)
    last_mw_id = cursor.lastrowid
    cursor.close()
    database.commit()

    gw = {'otherId': otherId,
          'version': version,
          'mw_id'  : last_mw_id,
        }
    skymaphits = skymaps.get_skymap_hits(database, gw, minmjd, maxmjd, verbose)
    nhits = len(skymaphits['diaObjectId'])
    if nhits > 0:
        skymaps.insert_skymap_hits(database, gw, skymaphits)

    return ''

def get_ra_dec(skymap_filename):
    skymap = QTable.read(skymap_filename)
    i = np.argmax(skymap['PROBDENSITY'])
    uniq = skymap[i]['UNIQ']

    level, ipix = ah.uniq_to_level_ipix(uniq)
    nside = ah.level_to_nside(level)

    ra, dec = ah.healpix_to_lonlat(ipix, nside, order='nested')
    return (ra.deg, dec.deg)

def handle_event(database, dir, otherId, minmjd, maxmjd, verbose=False):
    nhits = 0
    ningested = 0
    for version in os.listdir(dir+'/'+otherId):
        if version.startswith('20'):

            # Only look at GW alets whe havent seen before
            if not getDone(dir, otherId, version):
                # Set done flag so we dont come back
                setDone(dir, otherId, version)

                try:
                    message = insert_gw_alert(database, dir, otherId, version)
                except Exception as e:
                    print('Error inserting gw alert in database' + str(e))

                # message says why it was rejected
                if len(message) == 0:
                    ningested += 1
                    print(otherId, version, 'ingested')
                else:
                    print(otherId, version, 'not ingested:', message)

    return ningested

def mjd2date(mjd):
    date = datetime.strptime("1858/11/17", "%Y/%m/%d")
    date += timedelta(mjd)
    return date

def bytes2string(bytes):
    base64_bytes   = base64.b64encode(bytes)
    str = base64_bytes.decode('utf-8')
    return str

def string2bytes(str):
    base64_bytes  = str.encode('utf-8')
    bytes = base64.decodebytes(base64_bytes)
    return bytes

def read_moc(datadir, name):
    f = open(datadir + '/%s.moc' % name, 'rb')
    bytes = f.read()
    f.close()
    return bytes

def make_moc(mocbytes):
    inbuf = io.BytesIO(mocbytes)
    moc = MOC.from_fits(inbuf)
    return moc

def make_image(moc10, moc50, moc90):
    """ Makes an image of a skymap by laying down three mocs
        returning the resut as bytes that can be base64 encoded and put in the database
    """
    moc10 = make_moc(moc10)
    moc50 = make_moc(moc50)
    moc90 = make_moc(moc90)
    notmoc = moc10.complement()
    fig = plt.figure(111, figsize=(8, 5))
    with WCS(fig, fov=360 * u.deg, projection="AIT") as wcs:
        ax = fig.add_subplot(1, 1, 1, projection=wcs)
        notmoc.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="lightgray", linewidth=None)
        moc90.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="red",   linewidth=None)
        moc50.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="orange",linewidth=None)
        moc10.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="cyan",  linewidth=None)

    plt.grid(color="black", linestyle="dotted")
    outbuf = io.BytesIO()
    plt.savefig(outbuf, format='png', bbox_inches='tight', pad_inches=-0.85, dpi=200)
    bytes = outbuf.getvalue()
    outbuf.close()
    return bytes

def getDone(dir, otherId, version):
    """ Return True if an empty file 'done' is found in otherId/version directory
    """
    flag = '%s/%s/%s/done' % (dir, otherId, version)
    return os.path.isfile(flag)

def setDone(dir, otherId, version):
    """ Create an empty file 'done' is found in otherId/version directory
    """
    flag = '%s/%s/%s/done' % (dir, otherId, version)
    datadir = '%s/%s/%s' % (dir, otherId, version)
    os.system('touch ' + flag) 

if __name__ == "__main__":
    """ Intended to run in a cron to harvest GW alerts that appear in the directory
    """
    import sys
    from docopt import docopt
    args = docopt(__doc__)
#    print(args)

    if args['--maxmjd']: maxmjd = float(args['--maxmjd'])
    else:                maxmjd = skymaps.mjdnow()

    if args['--minmjd']: minmjd = float(args['--minmjd'])
    else:                minmjd = maxmjd - settings.GW_ACTIVE_DAYS

    dir = settings.GW_DIRECTORY  #  '/mnt/cephfs/lasair/mma/gw/'
    database = db_connect.remote()

    verbose = True
    ningested = 0
    for file in sorted(os.listdir(dir)):
        if file.startswith('S') or file.startswith('M'):
            otherId = file
            ningested += handle_event(database, dir, otherId, minmjd, maxmjd, verbose)
    print(ningested, 'event versions ingested')
