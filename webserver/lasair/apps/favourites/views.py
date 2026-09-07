"""Views for favouriting and hiding objects.

The mark endpoint lives here rather than in the object app because the whole
feature is owned by this app; every URLconf is mounted at the root, so the
`objects/` path and the owning app are independent.
"""
import json
import logging
import sys
sys.path.append('../common')

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from lasair.apps.db_schema.utils import get_schema_dict
from src import annotate_util, db_connect

log = logging.getLogger(__name__)

RESULT_CAP = 1000

FAVOURITES_ZEROTEXT = (
    'You have not favourited any objects yet. '
    'Click the star on any object page to add it here.')

HIDDEN_ZEROTEXT = (
    'You have not hidden any objects. Hiding an object removes it from your own '
    'filter results and email digests, but leaves it visible to everyone else. '
    'Click the archive icon on an object page to hide one.')


@require_POST
def object_mark(request, diaObjectId):
    """*set the signed-in user's mark on an object to favourite, hidden or none*

    **Key Arguments:**

    - `request` -- the original request, carrying `{"mark": "favourite"|"hidden"|null}`
    - `diaObjectId` -- the object being marked

    **Return:**

    - `response` -- JSON carrying the `diaObjectId` and the mark now held

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('objects/<int:diaObjectId>/mark/', views.object_mark, name='object_mark'),
        ...
    ]
    ```
    """
    # NOT @login_required: THAT WOULD REDIRECT AN AJAX CALL TO AN HTML LOGIN PAGE
    if not request.user.is_authenticated:
        loginUrl = '%s?next=%s' % (reverse('login'), reverse('object_detail', args=[diaObjectId]))
        return JsonResponse(
            {'detail': 'Authentication required', 'loginUrl': loginUrl}, status=403)

    try:
        body = json.loads(request.body or '{}')
    except ValueError:
        return JsonResponse({'detail': 'Request body is not JSON'}, status=400)

    mark = body.get('mark')
    if mark is not None and mark not in annotate_util.MARKS:
        return JsonResponse(
            {'detail': 'Not a mark: %s' % mark}, status=400)

    try:
        annotate_util.mark_object(request.user, diaObjectId, mark)
    except Exception as e:
        log.error('Could not mark object %s for %s: %s', diaObjectId, request.user.username, e)
        return JsonResponse({'detail': 'Could not save the mark'}, status=500)

    return JsonResponse({'diaObjectId': diaObjectId, 'mark': mark})


def marked_objects(topic, classification):
    """*fetch the objects one user has marked, most recently marked first*

    **Key Arguments:**

    - `topic` -- the user's tag topic, `tags_<username>`
    - `classification` -- `favourite` or `hidden`

    **Return:**

    - `table` -- a list of rows for the object list widget

    **Usage:**

    ```python
    table = marked_objects('tags_dave', 'favourite')
    ```
    """
    dateColumn = 'favourited' if classification == annotate_util.MARK_FAVOURITE else 'hidden since'

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT o.diaObjectId, o.ra, o.decl, '
    query += 'FORMAT(mjdnow()-o.lastDiaSourceMjdTai,1) AS "days since", '
    query += 'o.latest_psfFlux AS "latest flux", '
    query += 's.classification AS "predicted type", '
    query += 'a.timestamp AS "' + dateColumn + '" '
    query += 'FROM annotations AS a '
    query += 'JOIN objects AS o ON o.diaObjectId = a.diaObjectId '
    query += 'LEFT JOIN sherlock_classifications AS s ON s.diaObjectId = a.diaObjectId '
    query += 'WHERE a.topic = %s AND a.classification = %s '
    # EXPLICIT, BECAUSE THE DATATABLE ONLY AUTO-SORTS objectId AND Created COLUMNS
    query += 'ORDER BY a.timestamp DESC '
    query += 'LIMIT %s'
    cursor.execute(query, (topic, classification, RESULT_CAP))
    table = cursor.fetchall()
    msl.close()
    return table


def mark_list(request, classification, header, header_icon, desc, zerotext, export_name, mode):
    """*render one page of the objects a user has marked*

    **Key Arguments:**

    - `request` -- the original request
    - `classification` -- `favourite` or `hidden`
    - `header` -- the page heading
    - `header_icon` -- template path of the header icon, the same glyph as the mark button
    - `desc` -- the line under the heading
    - `zerotext` -- the empty state
    - `export_name` -- the file name for the export dropdown
    - `mode` -- `favourites` or `hidden`, which the template branches on

    **Return:**

    - `response` -- the rendered page
    """
    topic = annotate_util.tag_topic(request.user.username)
    table = marked_objects(topic, classification)

    count = len(table)
    if count == RESULT_CAP:
        messages.info(
            request,
            f'We are only displaying the first <b>{RESULT_CAP}</b> objects.')

    marks = {row['diaObjectId']: classification for row in table}

    schema = get_schema_dict('objects')
    if count:
        for k in table[0].keys():
            if k not in schema:
                schema[k] = 'custom column'

    return render(request, 'favourites/object_list.html', {
        'table': table,
        'count': count,
        'schema': schema,
        'marks': marks,
        'header': header,
        'header_icon': header_icon,
        'desc': desc,
        'zerotext': zerotext,
        'export_name': export_name,
        'mode': mode,
    })


@login_required
def favourites_list(request):
    """*display the objects the signed-in user has favourited*

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('favourites/', views.favourites_list, name='favourites'),
        ...
    ]
    ```
    """
    return mark_list(
        request,
        classification=annotate_util.MARK_FAVOURITE,
        header='Favourite Objects',
        header_icon='includes/icons/icon_star.html',
        desc='The objects you have favourited, most recently favourited first.',
        zerotext=FAVOURITES_ZEROTEXT,
        export_name='favourites',
        mode='favourites')


@login_required
def hidden_list(request):
    """*display the objects the signed-in user has hidden*

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('hidden/', views.hidden_list, name='hidden_objects'),
        ...
    ]
    ```
    """
    return mark_list(
        request,
        classification=annotate_util.MARK_HIDDEN,
        header='Hidden Objects',
        header_icon='includes/icons/icon_archive.html',
        desc=('The objects you have hidden. They are left out of your own filter '
              'results, search results and email digests, and stay visible to '
              'everybody else.'),
        zerotext=HIDDEN_ZEROTEXT,
        export_name='hidden-objects',
        mode='hidden')


@login_required
@require_POST
def unhide_all(request):
    """*clear every hidden mark the signed-in user holds*

    The escape hatch for a user who has hidden things and cannot find them.
    There is no favourites equivalent.

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('hidden/unhide-all/', views.unhide_all, name='unhide_all'),
        ...
    ]
    ```
    """
    topic = annotate_util.tag_topic(request.user.username)
    try:
        removed = annotate_util.delete_classification(topic, annotate_util.MARK_HIDDEN)
    except Exception as e:
        log.error('Could not unhide all for %s: %s', request.user.username, e)
        messages.error(request, 'Your hidden objects could not be cleared.')
        return redirect('hidden_objects')

    if removed:
        messages.success(request, f'{removed} objects are no longer hidden.')
    else:
        messages.info(request, 'You had no hidden objects to clear.')
    return redirect('hidden_objects')
