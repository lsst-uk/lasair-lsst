from src import bad_fits
import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MmaWatchmap
import tempfile
import io
import time
import json
import math
import datetime
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord
from subprocess import Popen, PIPE
from random import randrange
from lasair import settings as django_settings
from django.utils.text import slugify
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.shortcuts import render, get_object_or_404, redirect
from lasair.apps.db_schema.utils import get_schema_dict
from src import db_connect
import copy
import sys
from .utils import make_image_of_MOC
from lasair.utils import bytes2string, string2bytes
sys.path.append('../common')


@csrf_exempt
def mma_watchmap_index(request):
    """*return a list of mma_watchmaps*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('mma_watchmaps/', views.mma_watchmap_index, name='mma_watchmap_index'),
        ...
    ]
    ```           
    """
    mmaWatchmaps = MmaWatchmap.objects.all()
    d = {}
    for mw in list(mmaWatchmaps):
        namespace = mw.namespace
        c = mw.params['classification']

        # get the type with the largest probability
        max = 0.0
        for type in ['BBH', 'BNS', 'NSBH', 'Terrestrial']:
            if type in c and c[type] > max:
                max = c[type]
                mma_type = namespace + ':' + type

        # build data packet
        new = {'mw_id': mw.mw_id,
               'otherId': mw.otherId,
               'version': mw.version,
               'mocimage': mw.mocimage,
               'area90': mw.area90,
               'mma_type': mma_type,
               'event_date': mw.event_date
               }
        # get the latest version for each otherId
        if mw.otherId in d:
            if mw.version > d[mw.otherId]['version']:
                d[mw.otherId] = new
        else:
            d[mw.otherId] = new

    return render(request, 'mma_watchmap/mma_watchmap_index.html', {'mmaWatchmaps': d.values()})


def chop(x):
    if isinstance(x, float):
        return '%.2f' % x
    if not x:
        return ''
    return x


def mma_watchmap_detail(request, mw_id):
    """*return the resulting matches of a mma_watchmap*

    **Key Arguments:**

    - `request` -- the original request
    - `mw_id` -- UUID of the MmaWatchmap

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('mma_watchmaps/<int:mw_id>/', views.mma_watchmap_detail, name='mma_watchmap_detail'),
        ...
    ]
    ```           
    """

    # CONNECT TO DATABASE AND GET WATCHMAP
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    mma_watchmap = get_object_or_404(MmaWatchmap, mw_id=mw_id)

    resultCap = 100

    # GRAB P2 WATCHMAP MATCHES
    query_hit = f"""
SELECT
o.diaObjectId, 
h.probdens2, h.contour, 
o.lastDiaSourceMjdTai as "last detected",
o.firstDiaSourceMjdTai - m.event_tai as "t_GW",
o.r_psfFlux, o.g_psfFlux,
o.ra, o.decl
FROM mma_area_hits as h, objects AS o, mma_areas AS m
WHERE m.mw_id={mw_id} AND h.mw_id={mw_id} AND o.diaObjectId=h.diaObjectId
AND h.probdens3 is NULL
ORDER BY h.probdens2 DESC LIMIT {resultCap}
"""

    cursor.execute(query_hit)
    table2 = cursor.fetchall()

    if len(table2) > 0:
        maxprobdens2 = table2[0]['probdens2']
        for i in range(len(table2)):
            table2[i]['probdens2'] /= maxprobdens2
            if table2[i]['probdens2'] < 0.005:
                table2 = table2[:i]
                break
    newtable2 = []
    for r2 in table2:
        r = {'diaObjectId': r2['diaObjectId'],
             'probdens': chop(r2['probdens2']),
             'contour': r2['contour'],
             'last detected': r2['last detected'],
             't_GW': chop(r2['t_GW']),
             }
        if r2['gPSFluxMax'] and r2['gPSFluxMax'] > 0:
            r['mag_g'] = chop(31.4 - 2.5 * math.log10(r2['gPSFluxMax']))
        else:
            r['mag_g'] = ''

        if r2['rPSFluxMax'] and r2['rPSFluxMax'] > 0:
            r['mag_r'] = chop(31.4 - 2.5 * math.log10(r2['rPSFluxMax']))
        else:
            r['mag_r'] = ''

        r['ra'] = r2['ra']
        r['decl'] = r2['decl']
        newtable2.append(r)

    count = len(table2)
    schema2 = ['probdens', 'contour', 'last detected', 't_GW', 'mag_g', 'mag_r', 'ra', 'decl']

    if count == resultCap:
        limit = resultCap

        if django_settings.DEBUG:
            apiUrl = "https://lasair-lsst.readthedocs.io/en/develop/core_functions/rest-api.html"
        else:
            apiUrl = "https://lasair-lsst.readthedocs.io/en/main/core_functions/rest-api.html"
        messages.info(request, f"We are only displaying the first <b>{resultCap}</b> objects matched against this mma_watchmap. But don't worry! You can access all results via the <a class='alert-link' href='{apiUrl}' target='_blank'>Lasair API</a>.")
    else:
        limit = False

    # ADD SCHEMA
#    schema = get_schema_dict("objects")

#    if len(table2):
#        for k in table2[0].keys():
#            if k not in schema:
#                schema[k] = "custom column"

    # GRAB P3 WATCHMAP MATCHES
    query_hit = f"""
SELECT
o.diaObjectId, 
h.probdens3, h.contour, h.distance as dist,
o.lastDiaSourceMjdTai as "last detected",
o.firstDiaSourceMjdTai - m.event_tai as "t_GW",
s.classification, s.distance, s.z, s.photoZ, s.photoZerr,
o.r_psfFlux, o.g_psfFlux,
o.ra, o.decl 
FROM mma_area_hits as h, objects AS o, sherlock_classifications AS s, mma_areas AS m
WHERE m.mw_id={mw_id} AND h.mw_id={mw_id} 
AND o.diaObjectId=h.diaObjectId AND o.diaObjectId=s.diaObjectId
AND h.probdens3 is not NULL
ORDER BY h.probdens3 DESC LIMIT {resultCap}
"""

    cursor.execute(query_hit)
    table3 = cursor.fetchall()

    if len(table3) > 0:
        maxprobdens3 = table3[0]['probdens3']
        for i in range(len(table3)):
            table3[i]['probdens3'] /= maxprobdens3
            if table3[i]['probdens3'] < 0.005:
                table3 = table3[:i]
                break
    newtable3 = []
    for r3 in table3:
        r = {'diaObjectId': r3['diaObjectId'],
             'probdens': chop(r3['probdens3']),
             'contour': r3['contour'],
             'last detected': r3['last detected'],
             't_GW': chop(r3['t_GW']),
             'Sherlock': r3['classification'],
             }

        if r3['gPSFluxMax'] and r3['gPSFluxMax'] > 0:
            m = 23.9 - 2.5 * math.log10(r3['gPSFluxMax'])
            r['mag_g'] = chop(m)
            r['M_g'] = chop(m - 25 - 5 * math.log10(r3['dist']))
        else:
            r['mag_g'] = ''
            r['M_g'] = ''

        if r3['rPSFluxMax'] and r3['rPSFluxMax'] > 0:
            m = 23.9 - 2.5 * math.log10(r3['rPSFluxMax'])
            r['mag_r'] = chop(m)
            r['M_r'] = chop(m - 25 - 5 * math.log10(r3['dist']))
        else:
            r['mag_r'] = ''
            r['M_r'] = ''

        if r3['z']:
            r['z'] = r3['z']
            r['zerr'] = 0.0
            r['zflag'] = 'specz'
        elif r3['photoZ']:
            r['z'] = r3['photoZ']
            r['zerr'] = r3['photoZerr']
            r['zflag'] = 'photz'
        else:
            r['z'] = ''
            r['zerr'] = ''
            r['zflag'] = 'no_z'

        r['ra'] = r3['ra']
        r['decl'] = r3['decl']
        newtable3.append(r)

    schema3 = ['probdens', 'contour', 'last detected', 't_GW', 'Sherlock', 'mag_g', 'M_g', 'mag_r', 'M_r', 'z', 'zerr', 'zflag', 'ra', 'decl']

    if count == resultCap:
        limit = resultCap

        if django_settings.DEBUG:
            apiUrl = "https://lasair-lsst.readthedocs.io/en/develop/core_functions/rest-api.html"
        else:
            apiUrl = "https://lasair-lsst.readthedocs.io/en/main/core_functions/rest-api.html"
        messages.info(request, f"We are only displaying the first <b>{resultCap}</b> objects matched against this mma_watchmap. But don't worry! You can access all results via the <a class='alert-link' href='{apiUrl}' target='_blank'>Lasair API</a>.")
    else:
        limit = False

    return render(request, 'mma_watchmap/mma_watchmap_detail.html', {
        'mma_watchmap': mma_watchmap,
        'lasair_url': settings.LASAIR_URL,
        'table2': newtable2, 'schema2': schema2,
        'table3': newtable3, 'schema3': schema3,
        'count': count,
        'limit': limit})
