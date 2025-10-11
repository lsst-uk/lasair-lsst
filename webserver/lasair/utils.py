import sys
import os
import time
import json
import math
import ephem
import json
import base64

sys.path.append('../common')
from src import cutoutStore
from src import db_connect
import settings as lasair_settings

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.http import JsonResponse
#from django.conf import settings as django_settings

import dateutil.parser as dp
from datetime import datetime, timedelta
from datetime import date
import pandas as pd
from lasair.lightcurves import lightcurve_fetcher
from astropy.time import Time

def datetime_converter(o):
    """convert date to string

     **Key Arguments:**

    - `o` -- datetime object
    """
    if isinstance(o, datetime):
        return o.__str__()


def mjd_from_iso(date):
    """convert and return a Julian Date from ISO format date

     **Key Arguments:**

    - `date` -- date in iso format
    """
    if not date.endswith('Z'):
        date += 'Z'
    parsed_t = dp.parse(date)
    unix = int(parsed_t.strftime('%s'))
    mjd = unix / 86400 + 40587
    return mjd


def mjd_now():
    """*return the current UTC time as an MJD*

    **Usage:**

    ```python
    from lasair.apps.object import mjd_now
    mjd = mjd_now()
    ```           
    """
    return time.time() / 86400 + 40587.0


def ecliptic(ra, dec):
    """*return equatorial coordinates as ecliptic coordinates*

    **Usage:**

    ```python
    from lasair.apps.object import ecliptic
    ra, dec = ecliptic(ra, dec)
    ```           
    """
    np = ephem.Equatorial(math.radians(ra), math.radians(dec), epoch='2000')
    e = ephem.Ecliptic(np)
    return (math.degrees(e.lon), math.degrees(e.lat))


def rasex(ra):
    """*return ra in sexigesimal format*

    **Usage:**

    ```python
    from lasair.apps.object import rasex
    ra = rasex(ra)
    ```           
    """
    h = math.floor(ra / 15)
    ra -= h * 15
    m = math.floor(ra * 4)
    ra -= m / 4.0
    s = ra * 240
    return '%02d:%02d:%.3f' % (h, m, s)


def decsex(de):
    """*return dec in sexigesimal format*

    **Usage:**

    ```python
    from lasair.apps.object import decsex
    dec = decsex(dec)
    ```           
    """
    ade = abs(de)
    d = math.floor(ade)
    ade -= d
    m = math.floor(ade * 60)
    ade -= m / 60.0
    s = ade * 3600
    if de > 0.0:
        return '%02d:%02d:%.3f' % (d, m, s)
    else:
        return '-%02d:%02d:%.3f' % (d, m, s)


def objjson(diaObjectId, lite=False):
    """return all data for an object as a json object (`diaObjectId`,`objectData`,`diaSources`,`count_isdiffpos`,`count_all_diaSources`,`count_diaNonDetectionLimits`,`sherlock`,`TNS`, `annotations`)

    **Usage:**

    ```python
    from lasair.utils import objjson
    objectData = objjson(objID)
    ```  
    """
    objectData = None
    message = ''
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    if lite:
        query = 'SELECT nSources, ra, decl, firstDiaSourceMjdTai, lastDiaSourceMjdTai,glat,ebv '
    else:
        query = 'SELECT * '
    query += 'FROM objects WHERE diaObjectId = %s' % diaObjectId
    cursor.execute(query)
    for row in cursor:
        objectData = row

    if not objectData:
        return None

    now = mjd_now()
    if objectData:
#        if objectData and 'annotation' in objectData and objectData['annotation']:
#            objectData['annotation'] = objectData['annotation'].replace('"', '').strip()

        objectData['rasex'] = rasex(objectData['ra'])
        objectData['decsex'] = decsex(objectData['decl'])
        if objectData['firstDiaSourceMjdTai']:
            objectData['mjdmin'] = objectData['firstDiaSourceMjdTai']
        else:
            objectData['mjdmin'] = 60000

        if objectData['lastDiaSourceMjdTai']:
            objectData['mjdmax'] = objectData['lastDiaSourceMjdTai']
        else:
            objectData['mjdmax'] = 61000

        (ec_lon, ec_lat) = ecliptic(objectData['ra'], objectData['decl'])
        objectData['ec_lon'] = ec_lon
        objectData['ec_lat'] = ec_lat

        objectData['now_mjd'] = '%.2f' % now
        objectData['mjdmin_ago'] = now - objectData['mjdmin']
        objectData['mjdmax_ago'] = now - objectData['mjdmax']

    sherlock = {}
    query = 'SELECT * from sherlock_classifications WHERE diaObjectId = %s' % diaObjectId
    cursor.execute(query)
    for row in cursor:
        sherlock = row

    TNS = {}
    query = 'SELECT * '
    query += 'FROM crossmatch_tns JOIN watchlist_hits ON crossmatch_tns.tns_name = watchlist_hits.name '
    query += 'WHERE watchlist_hits.wl_id=%d AND watchlist_hits.diaObjectId=%s' % (lasair_settings.TNS_WATCHLIST_ID, diaObjectId)

    def ordinal_suffix(day):
        if 3 < day < 21 or 23 < day < 31:
            return 'th'
        else:
            return {1: 'st', 2: 'nd', 3: 'rd'}[day % 10]

    cursor.execute(query)
    for row in cursor:
        for k, v in row.items():
            if isinstance(v, datetime):
                suffix = ordinal_suffix(v.day)
                vstr = v.strftime(f"%-d{suffix} %B %Y at %H:%M:%S")
                mjd = Time([v], scale='utc').mjd[0]
                TNS[k] = vstr
                TNS[k + "_mjd"] = mjd
            elif k == "disc_int_name":
                TNS[k] = v.split(",")[0]
            elif v:
                TNS[k] = v

    LF = lightcurve_fetcher(cassandra_hosts=lasair_settings.CASSANDRA_HEAD)
    if lite:
        (diaSources, diaForcedSources) = LF.fetch(diaObjectId, lite=lite)
    else:
        (diaObject, diaSources, diaForcedSources) = LF.fetch(diaObjectId, lite=lite)
    LF.close()

    count_all_diaSources = len(diaSources)
    count_all_diaForcedSources = len(diaForcedSources)
    image_urls = {}
    for diaSource in diaSources:
        json_formatted_str = json.dumps(diaSource, indent=2)
        diaSource['json'] = json_formatted_str[1:-1]
        diaSource['mjd'] = mjd = float(diaSource['midpointMjdTai'])
        diaSource['since_now'] = mjd - now
        count_all_diaSources += 1
        diaSourceId = diaSource['diaSourceId']
        date = datetime.strptime("1858/11/17", "%Y/%m/%d")
        date += timedelta(mjd)
        diaSource['utc'] = date.strftime("%Y-%m-%d %H:%M:%S")

        # ADD IMAGE URLS
        diaSource['image_urls'] = {}
        for cutoutType in ['Science', 'Template', 'Difference']:
            diaSourceId_cutoutType = '%s_cutout%s' % (diaSourceId, cutoutType)
            url = 'https://%s/fits/%d/%s'
            url = url % (lasair_settings.LASAIR_URL, int(mjd), diaSourceId_cutoutType)
            diaSource['image_urls'][cutoutType] = url

    if count_all_diaSources == 0:
        return None

#    if not objectData:
#        ra = float(diaSource['ra'])
#        dec = float(diaSource['decl'])
#        objectData = {'ramean': ra, 'decmean': dec,
#                      'rasex': rasex(ra), 'decsex': decsex(dec),
#                      'ncand': len(diaSources), 'MPCname': ssnamenr}
#        objectData['annotation'] = 'Unknown object'

    message += 'Got %d diaSources' % count_all_diaSources

    diaSources.sort(key=lambda c: c['mjd'], reverse=True)

    detections = pd.DataFrame(diaSources)
    # SORT BY COLUMN NAME
    detections.sort_values(['mjd'], ascending=[True], inplace=True)

    # DISC MAGS
    objectData["discMjd"] = detections["mjd"].values[0]

    objectData["discUtc"] = detections["utc"].values[0]
    objectData["discMag"] = f"{detections['psfFlux'].values[0]:.2f}±{detections['psfFluxErr'].values[0]:.2f}"
    objectData["discFilter"] = detections['band'].values[0]

    # LATEST MAGS
    objectData["latestMjd"] = detections["mjd"].values[-1]
    objectData["latestUtc"] = detections["utc"].values[-1]

    objectData["latestMag"] = f"{detections['psfFlux'].values[-1]:.2f}±{detections['psfFluxErr'].values[-1]:.2f}"
    objectData["latestFilter"] = detections['band'].values[0]

    # PEAK MAG
    peakMag = detections[detections['psfFlux'] == detections['psfFlux'].min()]
    objectData["peakMjd"] = peakMag["mjd"].values[0]
    objectData["peakUtc"] = peakMag["utc"].values[0]
    objectData["peakMag"] = f"{peakMag['psfFlux'].values[0]:.2f}±{peakMag['psfFluxErr'].values[0]:.2f}"
    objectData["peakFilter"] = peakMag['band'].values[0]

    # annotations
    annotations = []
    query = 'SELECT annotationID, topic, version, timestamp, classification, explanation, classdict, url from annotations WHERE diaObjectId = %s' % diaObjectId
    cursor.execute(query)
    for row in cursor:
        annotations.append(row)
    for a in annotations:
        a['timestamp'] = a['timestamp'].strftime("%Y-%m-%d %H:%M:%S")

    data = {'diaObjectId': diaObjectId,
            'objectData': objectData,
            'diaSources': diaSources,
            'diaForcedSources': diaForcedSources,
            'sherlock': sherlock,
            'annotations': annotations,
            'image_urls': image_urls,
            'TNS': TNS, 'message': message}
    return data

def distance(ra1, de1, ra2, de2):
    """*calculate the distance in degrees between 2 points*

    **Key Arguments:**

    - `ra1` -- position 1 RA
    - `de1` -- position 1 Dec
    - `ra2` -- position 2 RA
    - `de2` -- position 2 Dec

    **Usage:**

    ```python
    from lasair.apps.search import distance
    separation = distance(ra1, de1, ra2, de2)
    ```           
    """
    dra = (ra1 - ra2) * math.cos(de1 * math.pi / 180)
    dde = (de1 - de2)
    return math.sqrt(dra * dra + dde * dde)


def bytes2string(bytes):
    """*convert byte to string and return*

    **Key Arguments:**

    - `bytes` -- the byte string to convert
    """
    base64_bytes = base64.b64encode(bytes)
    str = base64_bytes.decode('utf-8')
    return str


def string2bytes(str):
    """*convert string to bytes and return*

    **Key Arguments:**

    - `str` -- the str string to convert to string
    """
    base64_bytes = str.encode('utf-8')
    bytes = base64.decodebytes(base64_bytes)
    return bytes


def fits(request, candid_cutoutType):
    # cutoutType can be cutoutDifference, cutoutTemplate, cutoutScience
    osc = cutoutStore.cutoutStore()
    try:
        fitsdata = osc.getCutout(candid_cutoutType)
    except:
        fitsdata = ''

    response = HttpResponse(fitsdata, content_type='image/fits')
    response['Content-Disposition'] = 'attachment; filename="%s.fits"' % candid_cutoutType
    return response
