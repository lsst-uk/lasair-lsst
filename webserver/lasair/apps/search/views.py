from django.shortcuts import render
from .utils import conesearch_impl, readcone, sexra, sexde
import re
import settings
from src import db_connect
from lasair.apps.db_schema.utils import get_schema_dict
from astrocalc.coords import unit_conversion
from fundamentals.logs import emptyLogger
from django.db import connection
from gkutils.commonutils import coneSearchHTM, FULL, QUICK, CAT_ID_RA_DEC_COLS, base26, Struct


def search(
        request,
        query=False):
    """*return conesearch results (search data within request body)*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('conesearch/', views.conesearch, name='conesearch'),
        ...
    ]
    ```
    """
    if request.method == 'POST':
        query = request.POST['query']
    if query:
        results, schema = do_search(query)
        json_checked = False
        if 'json' in request.POST and request.POST['json'] == 'on':
            json_checked = True

        # data = conesearch_impl(query)
        if json_checked:
            return HttpResponse(json.dumps(results, indent=2), content_type="application/json")
        else:
            return render(request, 'search/search.html', {'results': results, 'schema': schema, 'query': query})
    else:
        return render(request, 'search/search.html', {'results': [], 'schema': [], 'query': ''})


def do_search(
    query
):
    """*determine the type of search the user is requesting*

    **Key Arguments:**

    - `query` -- the text query entered in to the search box

    **Usage:**

    ```python
    usage code
    ```
    """

    objectColumns = 'o.objectId, o.ramean,o.decmean, o.rmag, o.gmag, jdnow()-o.jdmax as "last detected (days ago)"'

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = query.strip()
    query = query.replace(",", " ")

    objectName = re.compile(r'(^[a-zA-Z]\S*|^.*[a-zA-Z]$)', re.S)
    objectMatch = objectName.match(query)

    queries = []
    results = []

    schema = get_schema_dict('objects')

    if objectMatch:
        objectName = objectMatch.group()

        queries.append(f"select {objectColumns} from objects o where o.objectId = '{objectName}'")
        queries.append(f"SELECT {objectColumns} FROM objects o, crossmatch_tns t, watchlist_cones w, watchlist_hits h where w.wl_id = {settings.TNS_WATCHLIST_ID} and w.cone_id=h.cone_id and h.objectId=o.objectId and t.tns_name = w.name and (w.name = '{objectName.replace('AT','').replace('SN','').replace('KN','')}' or LOCATE('{objectName}' ,t.disc_int_name))")
        # queries.append(f"SELECT {objectColumns} FROM objects o, watchlist_hits h where h.wl_id = {settings.TNS_WATCHLIST_ID} AND h.objectId=o.objectId AND h.name = '{objectName.replace('AT','').replace('SN','').replace('KN','')}' ")
        queries.append(f"SELECT {objectColumns} FROM objects o, sherlock_classifications s where s.objectId=o.objectId and o.objectId = '{objectName}'")

        for q in queries:
            cursor.execute(q)
            results += cursor.fetchall()
    else:
        # ASSUME THIS COULD BE A CONE SEARCH
        if "|" in query:
            squery = query.split("|")
            query = [q.strip() for q in squery]
        else:
            query = query.split()

        if len(query) in (2, 3):
            log = emptyLogger()
            # ASTROCALC UNIT CONVERTER OBJECT
            converter = unit_conversion(
                log=log
            )
            try:
                ra = converter.ra_sexegesimal_to_decimal(
                    ra=query[0]
                )
                dec = converter.dec_sexegesimal_to_decimal(
                    dec=query[1]
                )
            except:
                return [], []
        else:
            return [], []

        if len(query) == 3:
            radius = float(query[2])
        else:
            radius = 5.

        # Is there an object within RADIUS arcsec of this object? - KWS - need to fix the gkhtm code!!
        message, matches = coneSearchHTM(ra, dec, radius, 'objects', queryType=QUICK, conn=connection, django=True, prefix='htm', suffix='')
        objectIds = [o[1]['objectId'] for o in matches]
        objectIds = "','".join(objectIds)
        query = f"select {objectColumns} from objects o where o.objectId in ('{objectIds}')"
        cursor.execute(query)
        results += cursor.fetchall()

    # MAKE UNIQUE
    try:
        results = list({v['objectId']: v for v in results}.values())
    except:
        pass

    return results, schema

# use the tab-trigger below for new function
# xt-def-simple-function-template
