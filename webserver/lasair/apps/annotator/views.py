from src import db_connect
import sys
from django.contrib import messages
from django.shortcuts import render
from lasair.apps.annotator.models import Annotators
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from lasair.apps.db_schema.utils import get_schema_dict
from lasair.apps.favourites.utils import suppress_hidden
from .utils import add_annotator_metadata
sys.path.append('../common')


@csrf_exempt
def annotator_index(request):
    """*return a list of public and user owned annotators*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('annotator/', views.annotator_index, topic='annotator_index'),
        ...
    ]
    ```
    """

    # PUBLIC WATCHMAPS
    publicAnnotators = Annotators.objects.filter(public__gte=1)
    publicAnnotators = add_annotator_metadata(publicAnnotators, remove_duplicates=True)

    # USER WATCHMAPS
    if request.user.is_authenticated:
        myAnnotators = Annotators.objects.filter(user=request.user)
        myAnnotators = add_annotator_metadata(myAnnotators)
    else:
        myAnnotators = None

    return render(request, 'annotator/annotator_index.html',
                  {'myAnnotators': myAnnotators,
                   'publicAnnotators': publicAnnotators,
                   'authenticated': request.user.is_authenticated})


def annotator_detail(request, topic):
    """*return the resulting matches of a annotator*

    **Key Arguments:**

    - `request` -- the original request
    - `topic` -- UUID of the Annotator

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('annotator/<slug:topic>/', views.annotator_detail, topic='annotator_detail'),
        ...
    ]
    ```           
    """

    # CONNECT TO DATABASE AND GET WATCHMAP
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    annotator = get_object_or_404(Annotators, topic=topic)

    resultCap = 1000

    # IS USER ALLOWED TO SEE THIS RESOURCE?
    is_owner = (request.user.is_authenticated) and (request.user.id == annotator.user.id)
    is_public = (annotator.public > 0)
    is_visible = is_owner or is_public
    if not is_visible:
        messages.error(request, "This annotator is private and not visible to you")
        return render(request, 'error.html')

    # GRAB ALL ANNOTATOR MATCHES
    query_hit = f"""
SELECT 
o.diaObjectId, FORMAT(mjdnow()-o.lastDiaSourceMjdTai,1) as "days since",
a.classification, CAST(a.classdict as varchar(10000)) as classdict
FROM annotations AS a, objects AS o 
WHERE a.topic='{topic}' 
AND o.diaObjectId=a.diaObjectId 
LIMIT {resultCap}
"""

    cursor.execute(query_hit)
    table = cursor.fetchall()
    count = len(table)

    if count == resultCap:
        limit = resultCap
        messages.info(request, f"We are only displaying the first <b>{resultCap}</b> objects matched against this annotator. ")
    else:
        limit = False

    # HIDING MEANS "NEVER SHOW ME THIS AGAIN". THE EXCLUSION IS SCOPED TO THE
    # VIEWER, NOT THE ANNOTATOR OWNER, SO IT REACHES A PUBLIC ANNOTATOR SOMEBODY
    # ELSE OWNS. IT RUNS AFTER THE resultCap TEST ABOVE, WHICH ASKS WHETHER THE
    # QUERY ITSELF WAS CAPPED.
    table, marks, hidden_omitted = suppress_hidden(request.user, table)
    count = len(table)
    if hidden_omitted:
        messages.info(
            request,
            f"{hidden_omitted} of your hidden objects were left out of these results.")

    # ADD SCHEMA
    schema = get_schema_dict("annotations")

    if len(table):
        for k in table[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    return render(request, 'annotator/annotator_detail.html', {
        'annotator': annotator,
        'table': table,
        'marks': marks,
        'count': count,
        'schema': schema,
        'limit': limit})
