from src import db_connect
import sys
from django.contrib import messages
from django.shortcuts import render
from lasair.apps.community_resource.models import community_resource
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from lasair.apps.db_schema.utils import get_schema_dict
from .utils import add_annotator_metadata
sys.path.append('../common')


@csrf_exempt
def community_resource_index(request):
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


def community_resource_detail(request, resource_name):
    """*return the resulting matches of a community resource*

    **Key Arguments:**

    - `request` -- the original request
    - `resource_name` -- the unique name of the community resource

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('comres/<slug:resource_name>/', views.community_resource_detail, topic='community_resource_detail'),
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
o.diaObjectId, FORMAT(mjdnow()-o.maxTai,1) as "days since",
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

    # ADD SCHEMA
    schema = get_schema_dict("annotations")

    if len(table):
        for k in table[0].keys():
            if k not in schema:
                schema[k] = "custom column"

    return render(request, 'annotator/annotator_detail.html', {
        'annotator': annotator,
        'table': table,
        'count': count,
        'schema': schema,
        'limit': limit})
