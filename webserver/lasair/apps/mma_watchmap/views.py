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
import yaml
from yaml import CLoader as Loader
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

    # how many hits for each
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT mw_id, count(*) AS n FROM mma_assoc GROUP BY mw_id'
    cursor.execute(query)
    how_many = {}
    for row in cursor:
        how_many[row['mw_id']] = row['n']

    d = {}
    listd = None
    for mw in list(mmaWatchmaps):
        namespace = mw.namespace
        # build data packet
        packet = {'mw_id': mw.mw_id,
               'event_id': mw.event_id,
               'version': mw.version,
               'mocimage': mw.mocimage,
               'area90': mw.area90,
               'event_date': mw.event_date,
               'how_many': how_many.get(mw.mw_id, 0),
           }

        # get the type with the largest probability
        if namespace == 'LVK':
            max = 0.0
            c = mw.params['classification']
            for type in ['BBH', 'BNS', 'NSBH', 'Terrestrial']:
                if type in c and c[type] > max:
                    max = c[type]
                    packet['mma_type'] = namespace + ':' + type

            # get the latest version for each event_id
            if mw.event_id in d:
                if mw.version > d[mw.event_id]['version']:
                    d[mw.event_id] = packet
            else:
                d[mw.event_id] = packet

        elif namespace == 'ICC':
            packet['mma_type'] = 'ICC:' + mw.event_id
            d[mw.event_id] = packet

        elif namespace == 'ICGB':
            packet['mma_type'] = 'ICGB:' + mw.event_id
            d[mw.event_id] = packet
        else:
            continue

        lambda packet: packet['event_date']
        listd = sorted(d.values(), key=lambda packet: packet['event_date'], reverse=True)

    return render(request, 'mma_watchmap/mma_watchmap_index.html', {'mmaWatchmaps': listd})


def chop(x):
    if isinstance(x, float):
        return '%.2f' % x
    if not x:
        return ''
    return x


def yaml2text(mw):
    file = f'{settings.MMA_DIRECTORY}/{mw.namespace}/{mw.event_id}/{mw.version}/meta.yaml';
    yaml_text = open(file).read()
    data = yaml.load(yaml_text, Loader=Loader)
    lines = dict_to_text(data)
    return '\n'.join(lines)

def dict_to_text(d):
    suffices = {
        'area10'     : 'sq deg',
        'area50'     : 'sq deg',
        'area90'     : 'sq deg',
        'far'        : 'per year',
        'ENERGY'     : 'TeV',
        'FAR'        : 'per year',
        'DISTMEAN'   : 'Mpc',
        'DISTSTD'    : 'Mpc',
        'CIRC_ERR50' : 'degrees',
        'CIRC_ERR90' : 'degrees',
    }
    lines = []
    for k,_v in d.items():
        if isinstance(_v, list):
            v = str(_v)
        else:
            v = _v
        if isinstance(v, dict):
            lins = dict_to_text(v)
            for lin in lins:
                lines.append(f'{k} {lin}')
        else:
            if k in suffices:
                lines.append(f'{k} = {v} [{suffices[k]}]')
            else:
                lines.append(f'{k} = {v}')
    return lines

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
h.contour, 
o.lastDiaSourceMjdTai as "last detected",
h.delta_t as "delta_t",
o.latest_psfFlux, o.ra, o.decl
FROM mma_assoc as h, objects AS o, mma_events AS m
WHERE m.mw_id={mw_id} AND h.mw_id={mw_id} AND o.diaObjectId=h.diaObjectId
AND h.dist_host is NULL
ORDER BY h.contour LIMIT {resultCap}
"""

    cursor.execute(query_hit)
    table2 = cursor.fetchall()

    newtable2 = []
    for r2 in table2:
        r = {'diaObjectId': r2['diaObjectId'],
             'contour': r2['contour'],
             'last detected': r2['last detected'],
             'delta_t': chop(r2['delta_t']),
             'latest flux': r2['latest_psfFlux'],
             }

        r['ra'] = chop(r2['ra'])
        r['decl'] = chop(r2['decl'])
        newtable2.append(r)

    count = len(table2)
    schema2 = ['contour', 'last detected', 't_GW', 'latest flux', 'ra', 'decl']

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
h.contour, h.dist_host,
o.lastDiaSourceMjdTai as "last detected",
h.delta_t as "delta_t",
s.classification, s.distance, s.z, s.photoZ, s.photoZerr,
o.latest_psfFlux, o.absMag, o.ra, o.decl 
FROM mma_assoc as h, objects AS o, sherlock_classifications AS s, mma_events AS m
WHERE m.mw_id={mw_id} AND h.mw_id={mw_id} 
AND o.diaObjectId=h.diaObjectId AND o.diaObjectId=s.diaObjectId
AND h.dist_host is not NULL
ORDER BY h.dist_host DESC LIMIT {resultCap}
"""

    cursor.execute(query_hit)
    table3 = cursor.fetchall()

    newtable3 = []
    for r3 in table3:
        r = {'diaObjectId': r3['diaObjectId'],
             'dist_host': chop(r3['dist_host']),
             'contour': r3['contour'],
             'last detected': r3['last detected'],
             'delta_t': chop(r3['delta_t']),
             'Sherlock': r3['classification'],
             'latest flux': r3['latest_psfFlux'],
             }
        if r3['z']:
            r['z'] = r3['z']
            r['zflag'] = 'specz'
        elif r3['photoZ']:
            r['z'] = r3['photoZ']
            r['zflag'] = 'photz'
        else:
            r['z'] = ''
            r['zflag'] = 'no_z'
        if r3['absMag']:
            r['absMag'] = chop(r3['absMag'])
        else:
            r['absMag'] = ''

        r['ra'] = chop(r3['ra'])
        r['decl'] = chop(r3['decl'])
        newtable3.append(r)

    schema3 = ['contour', 'last detected', 't_GW', 'Sherlock', 'latest flux', 'absMag', 'z', 'zflag', 'ra', 'decl']

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
        'yaml2text': yaml2text(mma_watchmap),
        'lasair_url': settings.LASAIR_URL,
        'table2': newtable2, 'schema2': schema2,
        'table3': newtable3, 'schema3': schema3,
        'count': count,
        'limit': limit})
