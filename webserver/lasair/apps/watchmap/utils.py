import io
import base64
from mocpy import MOC, WCS
import matplotlib.pyplot as plt
from src import db_connect
import astropy.units as u
from django.shortcuts import render


def add_watchmap_metadata(
        watchmaps,
        remove_duplicates=False,
        filterFirstName=False,
        filterLastName=False):
    """*add extra metadata to the watchmap and return a list of watchmap dictionaries*

    **Key Arguments:**

    - `watchmaps` -- a list of watchmap objects
    - `remove_duplicates` -- remove duplicate watchmap. Default *False*
    - `filterFirstName` -- return only items belonging to specific user with this first name
    - `filterLastName` -- return only items belonging to specific user with this last name

    **Usage:**

    ```python
    watchmapDicts = add_watchmap_metadata(watchmap)
    ```           
    """

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)

    updatedWatchmap = []
    mocFiles = []
    for wmDict, wm in zip(watchmaps.values(), watchmaps):
        if wmDict["moc"] not in mocFiles or not remove_duplicates:
            if filterFirstName and filterFirstName.lower() != wm.user.first_name.lower():
                continue
            if filterLastName and filterLastName.lower() != wm.user.last_name.lower():
                continue

            # ADD LIST COUNT
            # wmDict['count'] = WatchlistCone.objects.filter(wm_id=wmDict['wm_id']).count()

            # ADD LIST USER
            wmDict['user'] = f"{wm.user.first_name} {wm.user.last_name}"
            wmDict['profile_image'] = wm.user.profile.image_b64
            updatedWatchmap.append(wmDict)
            mocFiles.append(wmDict["moc"])

            cursor.execute(f'SELECT count(*) AS count FROM area_hits WHERE ar_id={wmDict["ar_id"]}')
            for row in cursor:
                wmDict['count'] = row['count']
    return updatedWatchmap


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
    with WCS(fig, fov=360 * u.deg, projection="AIT") as wcs:
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
