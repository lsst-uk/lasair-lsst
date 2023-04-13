from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Watchmap
import tempfile
import io
import time
import json
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord
from mocpy import MOC, World2ScreenMPL
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
from .forms import WatchmapForm, UpdateWatchmapForm, DuplicateWatchmapForm
from .utils import make_image_of_MOC, add_watchmap_metadata
from lasair.utils import bytes2string, string2bytes
sys.path.append('../common')


@csrf_exempt
def watchmap_index(request):
    """*return a list of public and user owned watchmaps*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchmaps/', views.watchmap_index, name='watchmap_index'),
        ...
    ]
    ```           
    """
    # SUBMISSION OF NEW WATCHMAP
    if request.method == "POST":
        form = WatchmapForm(request.POST, request.FILES, request=request)

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

            if 'watchmap_file' in request.FILES:
                fits_bytes = (request.FILES['watchmap_file']).read()
                fits_string = bytes2string(fits_bytes)
                png_bytes = make_image_of_MOC(fits_bytes, request=request)
                png_string = bytes2string(png_bytes)

                wm = Watchmap(user=request.user, name=name, description=description,
                              moc=fits_string, mocimage=png_string, active=active, public=public)
                wm.save()
                watchmapname = form.cleaned_data.get('name')
                messages.success(request, f"The '{watchmapname}' watchmap has been successfully created")
                return redirect(f'watchmap_detail', wm.pk)
    else:
        form = WatchmapForm(request=request)

    # PUBLIC WATCHMAPS
    publicWatchmaps = Watchmap.objects.filter(public__gte=1)
    publicWatchmaps = add_watchmap_metadata(publicWatchmaps, remove_duplicates=True)

    # USER WATCHMAPS
    if request.user.is_authenticated:
        myWatchmaps = Watchmap.objects.filter(user=request.user)
        myWatchmaps = add_watchmap_metadata(myWatchmaps)
    else:
        myWatchmaps = None

    return render(request, 'watchmap/watchmap_index.html',
                  {'myWatchmaps': myWatchmaps,
                   'publicWatchmaps': publicWatchmaps,
                   'authenticated': request.user.is_authenticated,
                   'form': form})


def watchmap_detail(request, ar_id):
    """*return the resulting matches of a watchmap*

    **Key Arguments:**

    - `request` -- the original request
    - `ar_id` -- UUID of the Watchmap

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchmaps/<int:ar_id>/', views.watchmap_detail, name='watchmap_detail'),
        ...
    ]
    ```           
    """

    # CONNECT TO DATABASE AND GET WATCHMAP
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    watchmap = get_object_or_404(Watchmap, ar_id=ar_id)

    resultCap = 1000

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchmap.user.id)
    is_public = (watchmap.public and watchmap.public > 0)
    is_visible = is_owner or is_public
    if not is_visible:
        messages.error(request, "This watchmap is private and not visible to you")
        return render(request, 'error.html')

    if request.method == 'POST':
        form = UpdateWatchmapForm(request.POST, instance=watchmap, request=request)
        duplicateForm = DuplicateWatchmapForm(request.POST, instance=watchmap, request=request)

        action = request.POST.get('action')

    if request.method == 'POST' and is_owner and action == 'save':

        if action == "save":
            if form.is_valid():
                # UPDATING SETTINGS?
                if 'name' in request.POST:
                    watchmap.name = request.POST.get('name')
                    watchmap.description = request.POST.get('description')
                    if request.POST.get('active'):
                        watchmap.active = 1
                    else:
                        watchmap.active = 0

                    if request.POST.get('public'):
                        watchmap.public = 1
                    else:
                        watchmap.public = 0
                    watchmap.save()
                    messages.success(request, f'Your watchmap has been successfully updated')
    elif request.method == 'POST' and action == "copy":
        if duplicateForm.is_valid():
            oldName = copy.deepcopy(watchmap.name)
            name = request.POST.get('name')
            description = request.POST.get('description')
            newWm = watchmap
            newWm.pk = None
            newWm.user = request.user
            newWm.name = request.POST.get('name')
            newWm.description = request.POST.get('description')
            if request.POST.get('active'):
                newWm.active = True
            else:
                newWm.active = False

            if request.POST.get('public'):
                newWm.public = True
            else:
                newWm.public = False
            newWm.save()
            wm = newWm
            ar_id = wm.pk
            messages.success(request, f'You have successfully copied the "{oldName}" watchmap to My Watchmaps. The results table is initially empty, but should start to fill as new transient detections are found within the map area.')
            return redirect(f'watchmap_detail', ar_id)
    else:
        form = UpdateWatchmapForm(instance=watchmap, request=request)
        duplicateForm = DuplicateWatchmapForm(instance=watchmap, request=request)

    # GRAB ALL WATCHMAP MATCHES
    query_hit = f"""
SELECT
o.objectId, o.ramean,o.decmean, o.rmag, o.gmag, jdnow()-o.jdmax as "last detected (days ago)"
FROM area_hits as h, objects AS o
WHERE h.ar_id={ar_id}
AND o.objectId=h.objectId
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
        # WHERE h.ar_id={ar_id}
        # AND o.objectId=h.objectId
        # """
        # cursor.execute(countQuery)
        # count = cursor.fetchone()["count"]

        if settings.DEBUG:
            apiUrl = "https://lasair.readthedocs.io/en/develop/core_functions/rest-api.html"
        else:
            apiUrl = "https://lasair.readthedocs.io/en/main/core_functions/rest-api.html"
        messages.info(request, f"We are only displaying the first <b>{resultCap}</b> objects matched against this watchmap. But don't worry! You can access all results via the <a class='alert-link' href='{apiUrl}' target='_blank'>Lasair API</a>.")
    else:
        limit = False

    # ADD SCHEMA
    schema = get_schema_dict("objects")

    if len(table):
        for k in table[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    return render(request, 'watchmap/watchmap_detail.html', {
        'watchmap': watchmap,
        'table': table,
        'count': count,
        'schema': schema,
        'form': form,
        'duplicateForm': duplicateForm,
        'limit': limit})


@login_required
def watchmap_create(request):
    """*create a new Watchmap*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchmaps/create/', views.watchmap_create, name='watchmap_create'),
        ...
    ]
    ```           
    """
    # SUBMISSION OF NEW WATCHMAP
    if request.method == "POST":
        form = WatchmapForm(request.POST, request.FILES, request=request)
        if not form.is_valid():
            messages.error(request, f'{form.errors}')
            return redirect(f'watchmap_index')

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

            if 'watchmap_file' in request.FILES:
                fits_bytes = (request.FILES['watchmap_file']).read()
                fits_string = bytes2string(fits_bytes)
                png_bytes = make_image_of_MOC(fits_bytes, request=request)
                png_string = bytes2string(png_bytes)

                wm = Watchmap(user=request.user, name=name, description=description,
                              moc=fits_string, mocimage=png_string, active=active, public=public)
                wm.save()
                watchmapname = form.cleaned_data.get('name')
                messages.success(request, f"The '{watchmapname}' watchmap has been successfully created")
                return redirect(f'watchmap_detail', wm.pk)


def watchmap_download(request, ar_id):
    """*download the original watchmap file used to create the Watchmap*

    **Key Arguments:**

    - `request` -- the original request
    - `ar_id` -- UUID of the Watchmap

    **Usage:**

    ```python
    urlpatterns = [
        ...
         path('watchmaps/<int:ar_id>/file/', views.watchmap_download, name='watchmap_download'),
        ...
    ]
    ```           
    """
    watchmap = get_object_or_404(Watchmap, ar_id=ar_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchmap.user.id)
    is_public = (watchmap.public > 0)
    is_visible = is_owner or is_public
    if not is_visible:
        return render(request, 'error.html', {
            'message': "This watchmap is private and not visible to you"})

    moc = string2bytes(watchmap.moc)

    filename = slugify(watchmap.name) + '.fits'
    tmpfilename = tempfile.NamedTemporaryFile().name + '.fits'
    f = open(tmpfilename, 'wb')
    f.write(moc)
    f.close()

    r = HttpResponse(moc)
    r['Content-Type'] = "application/fits"
    r['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return r


@login_required
def watchmap_delete(request, ar_id):
    """*delete a watchmap

    **Key Arguments:**

    - `request` -- the original request
    - `ar_id` -- the watchmap UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchmaps/<int:ar_id>/delete/', views.watchmap_delete, name='watchmap_delete'),
        ...
    ]
    ```
    """
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    watchmap = get_object_or_404(Watchmap, ar_id=ar_id)
    name = watchmap.name

    # DELETE WATCHMAP
    if request.method == 'POST' and request.user.is_authenticated and watchmap.user.id == request.user.id and request.POST.get('action') == "delete":
        watchmap.delete()
        messages.success(request, f'The "{name}" watchmap has been successfully deleted')
    else:
        messages.error(request, f'You must be the owner to delete this watchmap')

    return redirect('watchmap_index')
