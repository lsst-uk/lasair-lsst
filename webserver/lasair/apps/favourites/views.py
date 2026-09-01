"""Views for favouriting and hiding objects.

The mark endpoint lives here rather than in the object app because the whole
feature is owned by this app; every URLconf is mounted at the root, so the
`objects/` path and the owning app are independent.
"""
import json
import logging
import sys

from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from src import annotate_util

sys.path.append('../common')

log = logging.getLogger(__name__)


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
