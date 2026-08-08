from src import db_connect
import sys
import json
from django.contrib import messages
from django.shortcuts import render
from lasair.apps.annotator.models import Annotators
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from lasair.apps.db_schema.utils import get_schema_dict
from .utils import add_annotator_metadata
sys.path.append('../common/src')
from annotate_util import insert_annotation_db, delete_annotation, classifications_for_object

@csrf_exempt
def addtag(request, diaObjectId, username, tag):
    topic = 'tags_' + username
    insert_annotation_db(diaObjectId, topic, tag)
    taglist = classifications_for_object(topic, diaObjectId)
    return HttpResponse(json.dumps(taglist), content_type="application/json")

@csrf_exempt
def removetag(request, diaObjectId, username, tag):
    topic = 'tags_' + username
    delete_annotation(diaObjectId, topic, tag)
    taglist = classifications_for_object(topic, diaObjectId)
    return HttpResponse(json.dumps(taglist), content_type="application/json")

@csrf_exempt
def tags_index(request):
    if not request.user.is_authenticated:
        messages.error(request, "Must be logged in to use the Tags system")
        return render(request, 'error.html')

    topic = 'tags_' + request.user.username
    query = 'SELECT classification AS tag, count(*) AS n FROM annotations '
    query += f'WHERE topic="{topic}" GROUP BY classification'

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    table = cursor.fetchall()
    return render(request, 'annotator/tags_index.html', 
       { 'table': table, 
        })

@csrf_exempt
def tags_detail(request, tag):
    if not request.user.is_authenticated:
        messages.error(request, "Must be logged in to use the Tags system")
        return render(request, 'error.html')

    topic = 'tags_' + request.user.username
#    query = 'SELECT diaObjectId FROM annotations WHERE '
#    query += f'topic="{topic}" AND classification="{tag}"'

    query  = 'SELECT objects.diaObjectId,  '
    query += 'FORMAT(mjdnow() - objects.lastDiaSourceMjdTai,1) as obj_last,  '
    query += 'FORMAT(mjdnow() - (UNIX_TIMESTAMP(annotations.timestamp) / 86400 + 40587),1) AS tag_age  '
    query += 'FROM objects,annotations  '
    query += 'WHERE objects.diaObjectId = annotations.diaObjectId '
    query += f'AND annotations.topic="{topic}" AND annotations.classification="{tag}"'

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    table = cursor.fetchall()
    return render(request, 'annotator/tags_detail.html', 
       { 'table': table,
        'tag': tag,
        })


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
