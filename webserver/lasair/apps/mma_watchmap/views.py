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
from .forms import MmaWatchmapForm, UpdateMmaWatchmapForm, DuplicateMmaWatchmapForm
from .utils import make_image_of_MOC, add_mma_watchmap_metadata
from lasair.utils import bytes2string, string2bytes
sys.path.append('../common')
from src import bad_fits

@csrf_exempt
def mma_watchmap_index(request):
    """*return a list of public and user owned mma_watchmaps*

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
    myMmaWatchmaps = []
    publicMmaWatchmaps = MmaWatchmap.objects.all()

    return render(request, 'mma_watchmap/mma_watchmap_index.html',
                  {'myMmaWatchmaps': myMmaWatchmaps,
                   'publicMmaWatchmaps': publicMmaWatchmaps})

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

    # GRAB ALL WATCHMAP MATCHES
    query_hit = f"""
SELECT
o.diaObjectId, o.ra,o.decl, o.rPSFluxMean, o.gPSFluxMean, tainow()-o.maxTai as "last detected (days ago)"
FROM mma_area_hits as h, objects AS o
WHERE h.mw_id={mw_id}
AND o.diaObjectId=h.diaObjectId
limit {resultCap}
"""

    cursor.execute(query_hit)
    table = cursor.fetchall()
    count = len(table)

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

    if len(table):
        for k in table[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    return render(request, 'mma_watchmap/mma_watchmap_detail.html', {
        'mma_watchmap': mma_watchmap,
        'table': table,
        'count': count,
        'schema': schema,
        'limit': limit})

def mma_watchmap_download(request, mw_id):
    """*download the original mma_watchmap file used to create the MmaWatchmap*

    **Key Arguments:**

    - `request` -- the original request
    - `mw_id` -- UUID of the MmaWatchmap

    **Usage:**

    ```python
    urlpatterns = [
        ...
         path('mma_watchmaps/<int:mw_id>/file/', views.mma_watchmap_download, name='mma_watchmap_download'),
        ...
    ]
    ```           
    """
    mma_watchmap = get_object_or_404(MmaWatchmap, mw_id=mw_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    moc10 = string2bytes(mma_watchmap.moc10)

    filename = slugify(mma_watchmap.name) + '.fits'
    tmpfilename = tempfile.NamedTemporaryFile().name + '.fits'
    f = open(tmpfilename, 'wb')
    f.write(moc)
    f.close()

    r = HttpResponse(moc)
    r['Content-Type'] = "application/fits"
    r['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return r


@login_required
def mma_watchmap_delete(request, mw_id):
    """*delete a mma_watchmap

    **Key Arguments:**

    - `request` -- the original request
    - `mw_id` -- the mma_watchmap UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('mma_watchmaps/<int:mw_id>/delete/', views.mma_watchmap_delete, name='mma_watchmap_delete'),
        ...
    ]
    ```
    """
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    mma_watchmap = get_object_or_404(MmaWatchmap, mw_id=mw_id)
    name = mma_watchmap.name

    messages.error(request, f'You must be the owner to delete this mma_watchmap')

    return redirect('mma_watchmap_index')
