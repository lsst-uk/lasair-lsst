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
    # SUBMISSION OF NEW WATCHMAP
    if request.method == "POST":
        form = MmaWatchmapForm(request.POST, request.FILES, request=request)

        if form.is_valid():
            # GET WATCHMAP PARAMETERS
            t = time.time()
#            name = request.POST.get('name')
#            description = request.POST.get('description')

            if request.POST.get('public'):
                public = True
            else:
                public = False
            if request.POST.get('active'):
                active = True
            else:
                active = False

            if 'mma_watchmap_file' in request.FILES:
                fits_stream = (request.FILES['mma_watchmap_file'])
                fits_message = bad_fits.bad_moc_stream(fits_stream)
                fits_stream.seek(0)
                if fits_message is not None:
                    messages.error(request, f'Bad FITS file: {fits_message}')
                    return render(request, 'error.html')

                fits_bytes = fits_stream.read()
                fits_string = bytes2string(fits_bytes)
                png_bytes = make_image_of_MOC(fits_bytes, request=request)
                png_string = bytes2string(png_bytes)
                expire = datetime.datetime.now() + datetime.timedelta(days=settings.ACTIVE_EXPIRE)

                wm = MmaWatchmap(moc10=fits_string, 
                        mocimage=png_string, active=active, public=public, date_expire=expire)
                wm.save()
                mma_watchmapname = form.cleaned_data.get('name')
                messages.success(request, f"The '{mma_watchmapname}' mma_watchmap has been successfully created")
                return redirect(f'mma_watchmap_detail', wm.pk)
    else:
        form = MmaWatchmapForm(request=request)

    myMmaWatchmaps = []
    publicMmaWatchmaps = MmaWatchmap.objects.all()

    return render(request, 'mma_watchmap/mma_watchmap_index.html',
                  {'myMmaWatchmaps': myMmaWatchmaps,
                   'publicMmaWatchmaps': publicMmaWatchmaps,
                   'form': form})


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

    if request.method == 'POST':
        form = UpdateMmaWatchmapForm(request.POST, instance=mma_watchmap, request=request)
        duplicateForm = DuplicateMmaWatchmapForm(request.POST, instance=mma_watchmap, request=request)

        action = request.POST.get('action')

    if request.method == 'POST' and is_owner and action == 'save':

        if action == "save":
            if form.is_valid():
                # UPDATING SETTINGS?
                if 'name' in request.POST:
                    mma_watchmap.name = request.POST.get('name')
                    mma_watchmap.description = request.POST.get('description')
                    if request.POST.get('active'):
                        mma_watchmap.active = 1
                    else:
                        mma_watchmap.active = 0

                    if request.POST.get('public'):
                        mma_watchmap.public = 1
                    else:
                        mma_watchmap.public = 0
                    mma_watchmap.date_expire = \
                        datetime.datetime.now() + datetime.timedelta(days=settings.ACTIVE_EXPIRE)
                    mma_watchmap.save()
                    messages.success(request, f'Your mma_watchmap has been successfully updated')
    elif request.method == 'POST' and action == "copy":
        if duplicateForm.is_valid():
            oldName = copy.deepcopy(mma_watchmap.name)
            name = request.POST.get('name')
            description = request.POST.get('description')
            newWm = mma_watchmap
            newWm.pk = None
            if request.POST.get('active'):
                newWm.active = True
            else:
                newWm.active = False

            if request.POST.get('public'):
                newWm.public = True
            else:
                newWm.public = False
            newWm.date_expire = \
                    datetime.datetime.now() + datetime.timedelta(days=settings.ACTIVE_EXPIRE)
            newWm.save()
            wm = newWm
            mw_id = wm.pk
            messages.success(request, f'You have successfully copied the "{oldName}" mma_watchmap to My MmaWatchmaps. The results table is initially empty, but should start to fill as new transient detections are found within the map area.')
            return redirect(f'mma_watchmap_detail', mw_id)
    else:
        form = UpdateMmaWatchmapForm(instance=mma_watchmap, request=request)
        duplicateForm = DuplicateMmaWatchmapForm(instance=mma_watchmap, request=request)

    # GRAB ALL WATCHMAP MATCHES
    query_hit = f"""
SELECT
o.diaObjectId, o.ra,o.decl, o.rPSFluxMean, o.gPSFluxMean, tainow()-o.maxTai as "last detected (days ago)"
FROM area_hits as h, objects AS o
WHERE h.mw_id={mw_id}
AND o.diaObjectId=h.diaObjectId
limit {resultCap}
"""

    cursor.execute(query_hit)
    table = cursor.fetchall()
    count = len(table)

    if count == resultCap:
        limit = resultCap
        # countQuery = f"""
        # SELECT count(*) as count
        # FROM area_hits as h, objects AS o
        # WHERE h.mw_id={mw_id}
        # AND o.objectId=h.objectId
        # """
        # cursor.execute(countQuery)
        # count = cursor.fetchone()["count"]

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
        'form': form,
        'duplicateForm': duplicateForm,
        'limit': limit})


@login_required
def mma_watchmap_create(request):
    """*create a new MmaWatchmap*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('mma_watchmaps/create/', views.mma_watchmap_create, name='mma_watchmap_create'),
        ...
    ]
    ```           
    """
    # SUBMISSION OF NEW WATCHMAP
    if request.method == "POST":
        form = MmaWatchmapForm(request.POST, request.FILES, request=request)
        if not form.is_valid():
            messages.error(request, f'{form.errors}')
            return redirect(f'mma_watchmap_index')

        if form.is_valid():
            # GET WATCHMAP PARAMETERS
            t = time.time()
            name = request.POST.get('name')
            description = request.POST.get('description')

            if request.POST.get('public'):
                public = True
            else:
                public = False
            if request.POST.get('active'):
                active = True
            else:
                active = False

            if 'mma_watchmap_file' in request.FILES:
                fits_bytes = (request.FILES['mma_watchmap_file']).read()
                fits_string = bytes2string(fits_bytes)
                png_bytes = make_image_of_MOC(fits_bytes, request=request)
                png_string = bytes2string(png_bytes)

                wm = MmaWatchmap(moc10=fits_string, mocimage=png_string, active=active, public=public)
                wm.save()
                mma_watchmapname = form.cleaned_data.get('name')
                messages.success(request, f"The '{mma_watchmapname}' mma_watchmap has been successfully created")
                return redirect(f'mma_watchmap_detail', wm.pk)


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
