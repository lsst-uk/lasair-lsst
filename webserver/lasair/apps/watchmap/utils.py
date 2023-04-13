import io
import base64
from mocpy import MOC, World2ScreenMPL
import matplotlib.pyplot as plt
from src import db_connect
import astropy.units as u
from django.shortcuts import render


def add_watchmap_metadata(
        watchlists,
        remove_duplicates=False):
    """*add extra metadata to the watchlists and return a list of watchlist dictionaries*

    **Key Arguments:**

    - `watchlists` -- a list of watchlist objects
    - `remove_duplicates` -- remove duplicate watchlists. Default *False*

    **Usage:**

    ```python
    watchlistDicts = add_watchmap_metadata(watchlists)
    ```           
    """

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)

    updatedWatchlists = []
    mocFiles = []
    for wlDict, wl in zip(watchlists.values(), watchlists):
        if wlDict["moc"] not in mocFiles or not remove_duplicates:
            # ADD LIST COUNT
            # wlDict['count'] = WatchlistCone.objects.filter(wl_id=wlDict['wl_id']).count()

            # ADD LIST USER
            wlDict['user'] = f"{wl.user.first_name} {wl.user.last_name}"
            wlDict['profile_image'] = wl.user.profile.image_b64
            updatedWatchlists.append(wlDict)
            mocFiles.append(wlDict["moc"])

            cursor.execute(f'SELECT count(*) AS count FROM area_hits WHERE ar_id={wlDict["ar_id"]}')
            for row in cursor:
                wlDict['count'] = row['count']
    return updatedWatchlists


def make_image_of_MOC(fits_bytes, request):
    """*generate a skyplot of the MOC file*

    **Key Arguments:**

    - `fits_bytes` -- to FITS file data
    """
    inbuf = io.BytesIO(fits_bytes)
    try:
        moc = MOC.from_fits(inbuf)
    except:
        return render(request, 'error.html', {'message': 'Cannot make MOC from given file'})

    notmoc = moc.complement()

    fig = plt.figure(111, figsize=(10, 5))
    with World2ScreenMPL(fig, fov=360 * u.deg, projection="AIT") as wcs:
        ax = fig.add_subplot(1, 1, 1, projection=wcs)
        notmoc.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="lightgray", linewidth=None)
        moc.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="red", linewidth=None)
        moc.border(ax=ax, wcs=wcs, alpha=1, color="red")

    plt.grid(color="black", linestyle="dotted")
    outbuf = io.BytesIO()
    plt.savefig(outbuf, format='png', bbox_inches='tight', dpi=200)
    bytes = outbuf.getvalue()
    outbuf.close()
    return bytes
