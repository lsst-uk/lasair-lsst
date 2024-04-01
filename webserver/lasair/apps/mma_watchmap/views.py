from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MmaWatchmap
import tempfile
import io
import time
import json
import datetime
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord
from subprocess import Popen, PIPE
from random import randrange
from lasair import settings
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
from src import bad_fits

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
        c = mw.params['classification']

        # get the type with the largest probability
        max = 0.0
        for type in ['BBH', 'BNS', 'NSBH', 'Terrestrial']:
            if c[type] > max:
                max = c[type]
                gwtype = type

        # build data packet
        new = {'mw_id':mw.mw_id, 
                'otherId': mw.otherId, 
                'version': mw.version, 
                'mocimage': mw.mocimage, 
                'area90':mw.area90, 
                'gwtype':gwtype, 
                'event_date':mw.event_date
                }
        # get the latest version for each otherId
        if mw.otherId in d:
            if mw.version > d[mw.otherId]['version']:
                d[mw.otherId] = new
        else:
            d[mw.otherId] = new

    return render(request, 'mma_watchmap/mma_watchmap_index.html', {'mmaWatchmaps': d.values()})

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

    resultCap = 1000

    # GRAB P2 WATCHMAP MATCHES
    query_hit = f"""
SELECT
o.diaObjectId, o.rPSFlux, o.gPSFlux, h.probdens2, tainow()-o.maxTai as "last detected (days ago)"
FROM mma_area_hits as h, objects AS o
WHERE h.mw_id={mw_id} AND o.diaObjectId=h.diaObjectId
AND h.probdens3 is NULL
ORDER BY h.probdens2 DESC LIMIT {resultCap}
"""

    cursor.execute(query_hit)
    table2 = cursor.fetchall()
    count = len(table2)

    if count == resultCap:
        limit = resultCap

        if settings.DEBUG:
            apiUrl = "https://lasair.readthedocs.io/en/develop/core_functions/rest-api.html"
        else:
            apiUrl = "https://lasair.readthedocs.io/en/main/core_functions/rest-api.html"
        messages.info(request, f"We are only displaying the first <b>{resultCap}</b> objects matched against this mma_watchmap. But don't worry! You can access all results via the <a class='alert-link' href='{apiUrl}' target='_blank'>Lasair API</a>.")
    else:
        limit = False

    # ADD SCHEMA
    schema = get_schema_dict("objects")

    if len(table2):
        for k in table2[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    # GRAB P3 WATCHMAP MATCHES
    query_hit = f"""
SELECT
o.diaObjectId, o.rPSFlux, o.gPSFlux, h.probdens3, tainow()-o.maxTai as "last detected (days ago)"
FROM mma_area_hits as h, objects AS o
WHERE h.mw_id={mw_id} AND o.diaObjectId=h.diaObjectId
AND h.probdens3 is not NULL
ORDER BY h.probdens3 DESC LIMIT {resultCap}
"""

    cursor.execute(query_hit)
    table3 = cursor.fetchall()
    count = len(table3)

    if count == resultCap:
        limit = resultCap

        if settings.DEBUG:
            apiUrl = "https://lasair.readthedocs.io/en/develop/core_functions/rest-api.html"
        else:
            apiUrl = "https://lasair.readthedocs.io/en/main/core_functions/rest-api.html"
        messages.info(request, f"We are only displaying the first <b>{resultCap}</b> objects matched against this mma_watchmap. But don't worry! You can access all results via the <a class='alert-link' href='{apiUrl}' target='_blank'>Lasair API</a>.")
    else:
        limit = False

    # ADD SCHEMA
    schema = get_schema_dict("objects")

    if len(table3):
        for k in table2[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    return render(request, 'mma_watchmap/mma_watchmap_detail.html', {
        'mma_watchmap': mma_watchmap,
        'table2': table2,
        'table3': table3,
        'count': count,
        'schema': schema,
        'limit': limit})
