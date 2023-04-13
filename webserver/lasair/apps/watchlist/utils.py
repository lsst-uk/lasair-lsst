

def handle_uploaded_file(f):
    """*handle the upload of a watchlist*

    **Key Arguments:**

    - `f` -- the upoloaded file

    **Usage:**

    ```python
    cones = handle_uploaded_file(request.FILES['cones_file'])
    ```           
    """
    return f.read().decode('utf-8')


def add_watchlist_metadata(
        watchlists,
        remove_duplicates=False):
    """*add extra metadata to the watchlists and return a list of watchlist dictionaries*

    **Key Arguments:**

    - `watchlists` -- a list of watchlist objects
    - `remove_duplicates` -- remove duplicate watchlists. Default *False*

    **Usage:**

    ```python
    watchlistDicts = add_watchlist_metadata(watchlists)
    ```           
    """
    from lasair.apps.watchlist.models import Watchlist, WatchlistCone
    updatedWatchlists = []
    dupCheck = []
    for wlDict, wl in zip(watchlists.values(), watchlists):
        uuid = f"{wlDict['name']},{wlDict['description']},{wlDict['radius']}"
        if uuid not in dupCheck or not remove_duplicates:
            # ADD LIST COUNT
            wlDict['count'] = WatchlistCone.objects.filter(wl_id=wlDict['wl_id']).count()

            # ADD LIST USER
            wlDict['user'] = f"{wl.user.first_name} {wl.user.last_name}"
            wlDict['profile_image'] = wl.user.profile.image_b64
            updatedWatchlists.append(wlDict)
            dupCheck.append(uuid)
    return updatedWatchlists
