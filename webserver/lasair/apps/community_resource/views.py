from lasair.apps.filter_query.utils import add_filter_query_metadata
from lasair.apps.watchmap.models import Watchmap
from lasair.apps.watchlist.models import Watchlist
from lasair.apps.watchlist.utils import add_watchlist_metadata
from lasair.apps.watchmap.utils import add_watchmap_metadata
from lasair.apps.filter_query.models import filter_query
from src import db_connect
import sys
from django.contrib import messages
from django.shortcuts import render
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

    # PUBLIC FILTERS
    publicFilters = filter_query.objects.filter(public__gte=1)
    publicFilters = add_filter_query_metadata(publicFilters, remove_duplicates=True, filterFirstName="Community", filterLastName="Resources")

    # PUBLIC WATCHLISTS
    publicWatchlists = Watchlist.objects.filter(public__gte=1)
    publicWatchlists = add_watchlist_metadata(publicWatchlists, remove_duplicates=True, filterFirstName="Community", filterLastName="Resources")

    # PUBLIC WATCHMAPS
    publicWatchmaps = Watchmap.objects.filter(public__gte=1)
    publicWatchmaps = add_watchmap_metadata(publicWatchmaps, remove_duplicates=True, filterFirstName="Community", filterLastName="Resources")

    # # USER WATCHMAPS
    # if request.user.is_authenticated:
    #     myAnnotators = Annotators.objects.filter(user=request.user)
    #     myAnnotators = add_annotator_metadata(myAnnotators)
    # else:
    #     myAnnotators = None

    return render(request, 'community_resource/community_resource_index.html',
                  {'publicFilters': publicFilters,
                   'publicWatchlists': publicWatchlists,
                   'publicWatchmaps': publicWatchmaps, })
