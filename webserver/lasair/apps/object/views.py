import time
import json
import math
import ephem
from datetime import datetime, timedelta
from lasair.lightcurves import lightcurve_fetcher
from lasair.apps.watchlist.models import Watchlist
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.shortcuts import render, get_object_or_404, HttpResponse
from src import db_connect
from src.objectStore import objectStore
import settings
import os
import sys
from astropy.time import Time
from lasair.utils import mjd_now, ecliptic, rasex, decsex, objjson
from .utils import object_difference_lightcurve
sys.path.append('../common')


def object_detail(request, objectId):
    """*display details of an individual transient object*

    **Key Arguments:**

    - `request` -- the original request
    - `objectId` -- the UUID of the object requested

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('objects/<slug:objectId>/', views.object_detail, name='object_detail'),
        ...
    ]
    ```           
    """
    data = objjson(objectId, full=True)

    if not data:
        return render(request, 'error.html',
                      {'message': 'Object %s not in database' % objectId})

    if 'sherlock' in data and 'classification' in data['sherlock']:
        data['sherlock']['classification_expanded'] = data['sherlock']['classification']
        for k, v in {"NT": "Nuclear Transient", "BS": "Bright Star", "VS": "Variable Star", "SN": "Supernova", "CV": "Cataclysmic Variable", "AGN": "AGN"}.items():
            if data['sherlock']['classification_expanded'] == k:
                data['sherlock']['classification_expanded'] = v
        if data['sherlock']['classification_expanded'] == "ORPHAN":
            data['sherlock']['description'] = "The transient is not obviously associated with any catalogued galaxy nor is it coincident with a known stellar source."
    data2 = data.copy()
    if 'sherlock' in data2:
        data2.pop('sherlock')

    return render(request, 'object/object_detail.html', {
        'data': data,
        'json_data': json.dumps(data2),
        'authenticated': request.user.is_authenticated,
        'lightcurveHtml': object_difference_lightcurve(data)
    })
