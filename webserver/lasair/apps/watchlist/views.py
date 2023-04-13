from django.contrib.auth.decorators import login_required
from .forms import WatchlistForm, UpdateWatchlistForm, DuplicateWatchlistForm
import time
import random
import json
from subprocess import Popen, PIPE
from lasair.apps.watchlist.models import Watchlist, WatchlistCone
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.shortcuts import render, get_object_or_404, redirect
import src.run_crossmatch as run_crossmatch
from django.conf import settings
from django.contrib import messages
from src import db_connect
import sys
import copy
from lasair.apps.db_schema.utils import get_schema_dict
from .utils import handle_uploaded_file, add_watchlist_metadata

sys.path.append('../common')


@csrf_exempt
def watchlist_index(request):
    """*Return list of all watchlists viewable by user*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/', views.watchlist_index, name='watchlist_index'),
        ...
    ]
    ```
    """

    # SUBMISSION OF NEW WATCHLIST
    if request.method == "POST":
        form = WatchlistForm(request.POST, request.FILES, request=request)

        if form.is_valid():
            # GET WATCHLIST PARAMETERS
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

            d_radius = request.POST.get('radius')
            cones = request.POST.get('cones_textarea')
            if 'cones_file' in request.FILES:
                cones = handle_uploaded_file(request.FILES['cones_file'])
            try:
                default_radius = float(d_radius)
            except:
                messages.error(request, f'Cannot parse default radius {d_radius}')

            cone_list = []
            for line in cones.split('\n'):
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue
                line = line.replace('|', ',')
                tok = line.split(',')
                if len(tok) < 3:
                    messages.error(request, f'Bad line (not RA,Dec,Name): {line}\n')
                    continue
                try:
                    ra = float(tok[0])
                    dec = float(tok[1])
                    objectId = tok[2].strip()
                    if len(tok) >= 4 and len(tok[3].strip()) > 0 and tok[3].strip().lower() != "none":
                        radius = float(tok[3])
                    else:
                        radius = None
                    cone_list.append([objectId, ra, dec, radius])
                except Exception as e:
                    messages.error(request, f'Bad line {len(cone_list)}: {line}\n{str(e)}')

            wl = Watchlist(user=request.user, name=name, description=description, active=active, public=public, radius=default_radius)
            wl.save()
            cones = []
            for cone in cone_list:
                name = cone[0].encode('ascii', 'ignore').decode()
                if name != cone[0]:
                    messages.info(request, 'Non-ascii characters removed from name %s --> %s<br/>' % (cone[0], name))
                wlc = WatchlistCone(wl=wl, name=name, ra=cone[1], decl=cone[2], radius=cone[3])
                cones.append(wlc)
            chunks = 1 + int(len(cones) / 50000)
            for i in range(chunks):
                WatchlistCone.objects.bulk_create(cones[(i * 50000): ((i + 1) * 50000)])

            watchlistname = form.cleaned_data.get('name')
            messages.success(request, f"The '{watchlistname}' watchlist has been successfully created")
            return redirect(f'watchlist_detail', wl.pk)

    else:
        form = WatchlistForm(request=request)

    # PUBLIC WATCHLISTS
    publicWatchlists = Watchlist.objects.filter(public__gte=1)
    publicWatchlists = add_watchlist_metadata(publicWatchlists, remove_duplicates=True)

    # USER WATCHLISTS
    if request.user.is_authenticated:
        myWatchlists = Watchlist.objects.filter(user=request.user)
        myWatchlists = add_watchlist_metadata(myWatchlists)
    else:
        myWatchlists = None

    return render(request, 'watchlist/watchlist_index.html',
                  {'myWatchlists': myWatchlists,
                   'publicWatchlists': publicWatchlists,
                   'authenticated': request.user.is_authenticated,
                   'form': form})


def watchlist_detail(request, wl_id):
    """*return the resulting matches of a watchlist*

    **Key Arguments:**

    - `request` -- the original request
    - `wl_id` -- the watchlist catlaogue UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/<int:wl_id>/', views.watchlist_detail, name='watchlist_detail'),
        ...
    ]
    ```
    """

    # CONNECT TO DATABASE AND GET WATCHLIST
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    watchlist = get_object_or_404(Watchlist, wl_id=wl_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchlist.user.id)
    is_public = (watchlist.public and watchlist.public > 0)
    is_visible = is_owner or is_public
    if not is_visible:
        messages.error(request, "This watchlist is private and not visible to you")
        return render(request, 'error.html')

    if request.method == 'POST':
        duplicateForm = DuplicateWatchlistForm(request.POST, instance=watchlist, request=request)
        form = UpdateWatchlistForm(request.POST, instance=watchlist, request=request)
        action = request.POST.get('action')

    if request.method == 'POST' and is_owner and action == 'save':
        # UPDATING SETTINGS?
        if action == 'save':
            if form.is_valid():
                watchlist.name = request.POST.get('name')
                watchlist.description = request.POST.get('description')

                if request.POST.get('active'):
                    watchlist.active = 1
                else:
                    watchlist.active = 0

                if request.POST.get('public'):
                    watchlist.public = 1
                else:
                    watchlist.public = 0

                watchlist.radius = float(request.POST.get('radius'))
                if watchlist.radius > 360:
                    watchlist.radius = 360
                watchlist.save()
                messages.success(request, f'Your watchlist has been successfully updated')
        # REQUEST TO REFRESH THE WATCHLIST MATCHES
        elif action == 'run':
            hits = run_crossmatch.run_crossmatch(msl, watchlist.radius, watchlist.wl_id)
            messages.success(request, f'{hits} crossmatches found')

    elif request.method == 'POST' and action == "copy":

        if duplicateForm.is_valid():

            oldName = copy.deepcopy(watchlist.name)
            name = request.POST.get('name')
            description = request.POST.get('description')
            newWl = watchlist
            newWl.pk = None
            newWl.user = request.user
            newWl.name = request.POST.get('name')
            newWl.description = request.POST.get('description')
            if request.POST.get('active'):
                newWl.active = True
            else:
                newWl.active = False

            if request.POST.get('public'):
                newWl.public = True
            else:
                newWl.public = False
            newWl.save()
            wl = newWl

            # COPY ALL CONES
            query = f"""CREATE TEMPORARY TABLE watchlist{wl_id} AS SELECT * FROM watchlist_cones  WHERE wl_id = {wl_id};
                ALTER TABLE watchlist{wl_id} MODIFY cone_id INT DEFAULT 0;
                UPDATE watchlist{wl_id} SET cone_id=NULL, wl_id={wl.pk};
                INSERT INTO watchlist_cones SELECT * FROM watchlist{wl_id};
                drop TEMPORARY table if exists watchlist{wl_id};"""

            queries = cursor.execute(query, multi=True)
            # ITERATE OVER QUERIES
            for i in queries:
                pass
            msl.commit()

            wl_id = wl.pk

            messages.success(request, f'You have successfully copied the "{oldName}" watchlist to My Watchlists. The results table is initially empty, but should start to fill as new transient detections match against sources in your watchlist.')
            return redirect(f'watchlist_detail', wl_id)
    else:
        duplicateForm = DuplicateWatchlistForm(instance=watchlist, request=request)
        form = UpdateWatchlistForm(instance=watchlist, request=request)

    # FIND THE COUNT OF WATCHLIST MATCHES
    cursor.execute('SELECT count(*) AS count FROM watchlist_cones WHERE wl_id=%d' % wl_id)
    for row in cursor:
        number_cones = row['count']

    resultCap = 1000

    # GRAB ALL WATCHLIST MATCHES
    query_hit = f"""
SELECT
h.name as "Catalogue ID", h.arcsec as "separation (arcsec)",c.cone_id, o.objectId, o.ramean,o.decmean, o.rmag, o.gmag, jdnow()-o.jdmax as "last detected (days ago)"
FROM watchlist_cones AS c
NATURAL JOIN watchlist_hits as h
NATURAL JOIN objects AS o
WHERE c.wl_id={wl_id} limit {resultCap}
"""

    cursor.execute(query_hit)
    table = cursor.fetchall()
    count = len(table)

    if count == resultCap:
        limit = resultCap
        # countQuery = f"""
        # SELECT count(*) as count
        # FROM objects AS o, watchlist_hits as h
        # WHERE h.wl_id={wl_id}
        # AND o.objectId=h.objectId
        # """
        # cursor.execute(countQuery)
        # count = cursor.fetchone()["count"]

        if settings.DEBUG:
            apiUrl = "https://lasair.readthedocs.io/en/develop/core_functions/rest-api.html"
        else:
            apiUrl = "https://lasair.readthedocs.io/en/main/core_functions/rest-api.html"
        messages.info(request, f"We are only displaying the first <b>{resultCap}</b> objects matched against this watchlist. But don't worry! You can access results via the <a class='alert-link' href='{apiUrl}' target='_blank'>Lasair API</a>.")
    else:
        limit = False

    # ADD SCHEMA
    schema = {**get_schema_dict("objects"), **get_schema_dict("watchlist_hits")}
    schema["Catalogue ID"] = schema["name"]
    schema["separation (arcsec)"] = schema["arcsec"]
    schema["last detected (days ago)"] = "When was object last detected"
    if len(table):
        for k in table[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    watchlist = get_object_or_404(Watchlist, wl_id=wl_id)
    return render(request, 'watchlist/watchlist_detail.html', {
        'watchlist': watchlist,
        'table': table,
        'count': count,
        'schema': schema,
        'form': form,
        'duplicateForm': duplicateForm,
        'number_cones': number_cones,
        'limit': limit
    })


def watchlist_download(request, wl_id):
    """*download the original watchlist*

    **Key Arguments:**

    - `request` -- the original request
    - `wl_id` -- the watchlist catlaogue UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/<int:wl_id>/cat/', views.watchlist_download, name='watchlist_download'),
        ...
    ]
    ```
    """

    # GET THE WATCHLIST FROM DATABASE
    watchlist = get_object_or_404(Watchlist, wl_id=wl_id)

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == watchlist.user.id)
    is_public = (watchlist.public > 0)
    is_visible = is_owner or is_public
    if not is_visible:
        messages.error(request, "This watchlist is private and not visible to you")
        return render(request, 'error.html')

    msl = db_connect.remote()

    s = []
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute('SELECT name FROM watchlists WHERE wl_id=%d' % wl_id)
    name = cursor.fetchall()[0]["name"].replace(" ", "_") + "_watchlist_original.csv"

    cursor.execute('SELECT ra, decl, name, radius FROM watchlist_cones WHERE wl_id=%d LIMIT 10000' % wl_id)
    cones = cursor.fetchall()
    content = []
    content[:] = [','.join(str(value) for value in c.values()) for c in cones]
    content = '\n'.join(content)

    response = HttpResponse(content, content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{name}"'
    return response


@ login_required
def watchlist_delete(request, wl_id):
    """*delete a watchlist

    **Key Arguments:**

    - `request` -- the original request
    - `wl_id` -- the watchlist UUID

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('watchlists/<int:wl_id>/delete/', views.watchlist_delete, name='watchlist_delete'),
        ...
    ]
    ```
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    watchlist = get_object_or_404(Watchlist, wl_id=wl_id)
    name = watchlist.name

    # DELETE WATCHLIST
    if request.method == 'POST' and request.user.is_authenticated and watchlist.user.id == request.user.id and request.POST.get('action') == "delete":
        # DELETE ALL THE CONES OF THIS WATCHLIST
        WatchlistCone.objects.filter(wl_id=wl_id).delete()
        # DELETE ALL THE HITS OF THIS WATCHLIST
        query = 'DELETE from watchlist_hits WHERE wl_id=%d' % wl_id
        cursor.execute(query)
        msl.commit()
        # DELETE THE WATCHLIST
        watchlist.delete()
        messages.success(request, f'The "{name}" watchlist has been successfully deleted')
    else:
        messages.error(request, f'You must be the owner to delete this watchlist')

    return redirect('watchlist_index')
