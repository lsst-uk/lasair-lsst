from django.contrib import messages
from lasair.apps.favourites.utils import marks_for_table, suppress_hidden
from django.http import JsonResponse
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

DEFAULT_CONE_RADIUS = 5.

# ROUTING ALLOW-LIST FOR OBJECT NAMES. EVERY VALUE IS BOUND AS A PARAMETER, SO THIS ONLY DECIDES
# WHICH QUERIES ARE NAME SEARCHES. ANYTHING ELSE IS TREATED AS A CONE SEARCH. IT MATCHES:
# - A diaObjectId (17-22 DIGITS)
# - A TNS NAME WITH AN OPTIONAL AT/SN/KN PREFIX IN ANY CASE (2026abc, at 2026abc, SN2026abc)
# - A PARTIAL DISCOVERY NAME THAT STARTS WITH DIGITS (21abc, 123abc)
# - AN INTERNAL DISCOVERY NAME (ZTF21abcdefg, PS1-13abc), WITH SINGLE INTERNAL SPACES (Gaia 21abc)
# NO ALTERNATIVE STARTS WITH A NUMBER PAIR WITHOUT A LETTER, SO PLAIN AND SEXAGESIMAL COORDINATES
# NEVER MATCH.
OBJECT_NAME = re.compile(
    r'\d{17,22}'
    r'|(?i:(?:AT|SN|KN)\s?)?\d{4}[a-zA-Z]+'
    r'|\d+[a-zA-Z][\w.+:\-]*'
    r'|[a-zA-Z][\w.+:\-]*(?: [\w.+:\-]+)*',
    re.ASCII)
TNS_PREFIX = re.compile(r'^(?:AT|SN|KN)\s?(?=\d{4}[a-zA-Z]+$)', re.I | re.ASCII)


def search(
        request,
        query=False):
    """*return conesearch results (search data within request body)*

    **Key Arguments:**

    - `request` -- the original request (the query is read from GET, then POST)

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('conesearch/', views.conesearch, name='conesearch'),
        ...
    ]
    ```
    """
    # GET MAKES SEARCHES BOOKMARKABLE; POST IS KEPT FOR OLD CALLERS
    params = request.GET if request.GET.get('query') else request.POST
    query = params.get('query', query)
    if query:
        results, schema = do_search(query)
        json_checked = params.get('json') == 'on'

        # data = conesearch_impl(query)
        # HIDING MEANS "NEVER SHOW ME THIS AGAIN", AND SEARCH IS ONE OF THE PLACES
        # THE UI AND THE API DOCUMENTATION PROMISE IT REACHES
        results, marks, omitted = suppress_hidden(request.user, results)
        if omitted:
            messages.info(request, f"{omitted} of your hidden objects were left out of these results.")

        if json_checked:
            return JsonResponse(results, safe=False, json_dumps_params={'indent': 2})
        else:
            return render(request, 'search/search.html', {
                'results': results, 'schema': schema, 'query': query,
                'marks': marks})
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

    objectColumns = 'o.diaObjectId, o.ra,o.decl, mjdnow()-o.lastDiaSourceMjdTai as "last detected (days ago)"'

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = query.strip()
    query = query.replace(",", " ")

    results = []

    schema = get_schema_dict('objects')

    if OBJECT_NAME.fullmatch(query):
        tnsName = TNS_PREFIX.sub('', query)
        tnsQuery = (
            f"SELECT {objectColumns} FROM objects o, crossmatch_tns t, watchlist_cones w, watchlist_hits h where w.wl_id = %s and w.cone_id=h.cone_id and h.diaObjectId=o.diaObjectId and t.tns_name = w.name and (w.name = %s or LOCATE(%s ,t.disc_int_name))",
            (settings.TNS_WATCHLIST_ID, tnsName, query))
        queries = [tnsQuery]
        # ONLY AN ALL-DIGITS NAME CAN BE A diaObjectId, AND IT IS BOUND AS AN INTEGER SO
        # MYSQL NEVER COMPARES A STRING WITH THE BIGINT COLUMN
        if query.isascii() and query.isdigit():
            objectId = int(query)
            queries = [
                (f"select {objectColumns} from objects o where o.diaObjectId = %s", (objectId,)),
                tnsQuery,
                (f"SELECT {objectColumns} FROM objects o, sherlock_classifications s where s.diaObjectId=o.diaObjectId and o.diaObjectId = %s", (objectId,)),
            ]

        for sql, params in queries:
            cursor.execute(sql, params)
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
                radius = float(query[2]) if len(query) == 3 else DEFAULT_CONE_RADIUS
            except:
                return [], []
        else:
            return [], []

        # Is there an object within RADIUS arcsec of this object? - KWS - need to fix the gkhtm code!!
        message, matches = coneSearchHTM(ra, dec, radius, 'objects', queryType=QUICK, conn=connection, django=True, prefix='htm', suffix='')
        diaObjectIds = [int(o[1]['diaObjectId']) for o in matches]
        if diaObjectIds:
            placeholders = ",".join(["%s"] * len(diaObjectIds))
            cursor.execute(
                f"select {objectColumns} from objects o where o.diaObjectId in ({placeholders})",
                tuple(diaObjectIds))
            results += cursor.fetchall()

    # MAKE UNIQUE
    try:
        results = list({v['diaObjectId']: v for v in results}.values())
    except:
        pass

    return results, schema

# use the tab-trigger below for new function
# xt-def-simple-function-template
