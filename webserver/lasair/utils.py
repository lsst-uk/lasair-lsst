from src import objectStore
import sys
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.http import JsonResponse
import dateutil.parser as dp
from datetime import datetime, timedelta
import time
import json
import math
import ephem
import json
import pandas as pd
import base64
from src import db_connect
from datetime import date
import settings
from lasair.lightcurves import lightcurve_fetcher
from astropy.time import Time
sys.path.append('../../common')


def datetime_converter(o):
    """convert date to string

     **Key Arguments:**

    - `o` -- datetime object
    """
    if isinstance(o, datetime):
        return o.__str__()


def jd_from_iso(date):
    """convert and return a Julian Date from ISO format date

     **Key Arguments:**

    - `date` -- date in iso format
    """
    if not date.endswith('Z'):
        date += 'Z'
    parsed_t = dp.parse(date)
    unix = int(parsed_t.strftime('%s'))
    jd = unix / 86400 + 2440587.5
    return jd


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


def objjson(objectId, full=False):
    """return all data for an object as a json object (`objectId`,`objectData`,`candidates`,`count_isdiffpos`,`count_all_candidates`,`count_noncandidate`,`sherlock`,`TNS`)

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
    query = 'SELECT ncand, ramean, decmean, glonmean, glatmean, jdmin, jdmax '
    query += 'FROM objects WHERE objectId = "%s"' % objectId
    cursor.execute(query)
    for row in cursor:
        objectData = row

    if not objectData:
        return None

    now = mjd_now()
    if objectData:
        if objectData and 'annotation' in objectData and objectData['annotation']:
            objectData['annotation'] = objectData['annotation'].replace('"', '').strip()

        objectData['rasex'] = rasex(objectData['ramean'])
        objectData['decsex'] = decsex(objectData['decmean'])

        (ec_lon, ec_lat) = ecliptic(objectData['ramean'], objectData['decmean'])
        objectData['ec_lon'] = ec_lon
        objectData['ec_lat'] = ec_lat

        objectData['now_mjd'] = '%.2f' % now
        objectData['mjdmin_ago'] = now - (objectData['jdmin'] - 2400000.5)
        objectData['mjdmax_ago'] = now - (objectData['jdmax'] - 2400000.5)

    sherlock = {}
    query = 'SELECT * from sherlock_classifications WHERE objectId = "%s"' % objectId
    cursor.execute(query)
    for row in cursor:
        sherlock = row

    TNS = {}
    query = 'SELECT * '
    query += 'FROM crossmatch_tns JOIN watchlist_hits ON crossmatch_tns.tns_name = watchlist_hits.name '
    query += 'WHERE watchlist_hits.wl_id=%d AND watchlist_hits.objectId="%s"' % (settings.TNS_WATCHLIST_ID, objectId)

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

    LF = lightcurve_fetcher(cassandra_hosts=settings.CASSANDRA_HEAD)
    candidates = LF.fetch(objectId, full=full)
    LF.close()

    count_isdiffpos = count_all_candidates = count_noncandidate = 0
    image_store = objectStore.objectStore(suffix='fits', fileroot=settings.IMAGEFITS)
    image_urls = {}
    for cand in candidates:
        json_formatted_str = json.dumps(cand, indent=2)
        cand['json'] = json_formatted_str[1:-1]
        cand['mjd'] = mjd = float(cand['jd']) - 2400000.5
        cand['since_now'] = mjd - now
        if 'candid' in cand:
            count_all_candidates += 1
            candid = cand['candid']
            date = datetime.strptime("1858/11/17", "%Y/%m/%d")
            date += timedelta(mjd)
            cand['utc'] = date.strftime("%Y-%m-%d %H:%M:%S")

            # ADD IMAGE URLS
            cand['image_urls'] = {}
            for cutoutType in ['Science', 'Template', 'Difference']:
                candid_cutoutType = '%s_cutout%s' % (candid, cutoutType)
                filename = image_store.getFileName(candid_cutoutType)
                if 1 == 1 or os.path.exists(filename):
                    url = filename.replace(
                        '/mnt/cephfs/lasair',
                        f'https://{settings.LASAIR_URL}/lasair/static')
                    cand['image_urls'][cutoutType] = url

            if 'ssnamenr' in cand:
                ssnamenr = cand['ssnamenr']
                if ssnamenr == 'null':
                    ssnamenr = None
            if cand['isdiffpos'] == 't' or cand['isdiffpos'] == '1':
                count_isdiffpos += 1
        else:
            count_noncandidate += 1
            cand['magpsf'] = cand['diffmaglim']

    if count_all_candidates == 0:
        return None

    if not objectData:
        ra = float(cand['ra'])
        dec = float(cand['dec'])
        objectData = {'ramean': ra, 'decmean': dec,
                      'rasex': rasex(ra), 'decsex': decsex(dec),
                      'ncand': len(candidates), 'MPCname': ssnamenr}
        objectData['annotation'] = 'Unknown object'
        if row['ssdistnr'] > 0 and row['ssdistnr'] < 10:
            objectData['MPCname'] = ssnamenr

    message += 'Got %d candidates and %d noncandidates' % (count_all_candidates, count_noncandidate)

    candidates.sort(key=lambda c: c['mjd'], reverse=True)

    df = pd.DataFrame(candidates)
    # SORT BY COLUMN NAME
    df.sort_values(['mjd'],
                   ascending=[True], inplace=True)

    detections = df.loc[(df['candid'] > 0)]

    # DISC MAGS
    objectData["discMjd"] = detections["mjd"].values[0]
    objectData["discUtc"] = detections["utc"].values[0]
    objectData["discMag"] = f"{detections['magpsf'].values[0]:.2f}±{detections['sigmapsf'].values[0]:.2f}"
    if detections['fid'].values[0] == 1:
        objectData["discFilter"] = "g"
    else:
        objectData["discFilter"] = "r"

    # LATEST MAGS
    objectData["latestMjd"] = detections["mjd"].values[-1]
    objectData["latestUtc"] = detections["utc"].values[-1]
    objectData["latestMag"] = f"{detections['magpsf'].values[-1]:.2f}±{detections['sigmapsf'].values[-1]:.2f}"
    if detections['fid'].values[-1] == 1:
        objectData["latestFilter"] = "g"
    else:
        objectData["latestFilter"] = "r"

    # PEAK MAG
    peakMag = detections[detections['magpsf'] == detections['magpsf'].min()]
    objectData["peakMjd"] = peakMag["mjd"].values[0]
    objectData["peakUtc"] = peakMag["utc"].values[0]
    objectData["peakMag"] = f"{peakMag['magpsf'].values[0]:.2f}±{peakMag['sigmapsf'].values[0]:.2f}"
    if peakMag['fid'].values[0] == 1:
        objectData["peakFilter"] = "g"
    else:
        objectData["peakFilter"] = "r"

    data = {'objectId': objectId,
            'objectData': objectData,
            'candidates': candidates,
            'count_isdiffpos': count_isdiffpos,
            'count_isdiffneg': count_all_candidates - count_isdiffpos,
            'count_all_candidates': count_all_candidates,
            'count_noncandidate': count_noncandidate,
            'sherlock': sherlock,
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
    image_store = objectStore.objectStore(suffix='fits', fileroot=settings.IMAGEFITS, double=True)
    try:
        fitsdata = image_store.getFileObject(candid_cutoutType)
    except:
        fitsdata = ''

    response = HttpResponse(fitsdata, content_type='image/fits')
    response['Content-Disposition'] = 'attachment; filename="%s.fits"' % candid_cutoutType
    return response
