import json
from django.shortcuts import render
import src.date_nid as date_nid
import src.manage_status as manage_status
import settings
from astropy.time import Time
import datetime


def status_today(request):
    """*return staus report for today*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('status/<int:nid>/', views.status, name='status'),
        ...
    ]
    ```           
    """
    nid = date_nid.nid_now()
    return status(request, nid)


def status(request, nid):
    """*return staus report for a specific night*

    **Key Arguments:**

    - `request` -- the original request
    - `nid` -- the night ID to return status for (days since 2017-01-01)

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('status/<int:nid>/', views.status, name='status'),
        ...
    ]
    ```           
    """
    web_domain = settings.WEB_DOMAIN
    ms = manage_status.manage_status()
    status = ms.read(nid)

    statusSchema = {
        'nid'              : 'Night number (nid)',
        'update_time'      : 'Last Lasair update time',
        'today_lsst'       : 'Alerts sent by LSST today',
        'min_delay'        : 'Hours since most recent alert',
        'today_alert'      : 'Alerts received today',
        'diaObject'        : 'Objects received',
        'SSObject'         : 'SS objects received',
        'diaSource'        : 'Detections received',
        'diaSourceDB'      : 'Detections inserted into Cassandra',
        'diaForcedSource'  : 'Forced detections received',
        'diaForcedSourceDB': 'Forced detections inserted into Cassandra',
        'today_filter'     : 'Alerts received by Filter stage today',
        'today_filter_out' : 'Alerts sent to MySQL today',
        'today_database'   : 'Updated objects in database today',
        'total_count'      : "Total objects in database",

        'icassandra'       :'icassandra time today',
        'icutout'          :'icutout time today',
        'ifuture'          :'ifuture time today',
        'ikconsume'        :'ikconsume time today',
        'ikproduce'        :'ikproduce time today',
        'itotal'           :'ingest total time today',
        'ffeatures'        :'features time today'),
        'fwatchlist'       :'watchlist time today'),
        'fwatchmap'        :'watchmap time today'),
        'fmmagw'           :'mmagw time today'),
        'ffilters'         :'filters time today'),
        'ftransfer'        :'transfer time today'),
        'ftotal'           :'total filter time today'),
    }

    for k,v in statusSchema.items():
        if k in status:
            statusTable.append((v, status(k))

    date = date_nid.nid_to_date(nid)

    d0 = datetime.date(2017, 1, 1)
    d1 = d0 + datetime.timedelta(days=nid)
    d1 = datetime.datetime.combine(d1, datetime.datetime.min.time())

    mjd = Time([d1], scale='utc').mjd[0]

    prettyDate = date_nid.nid_to_pretty_date(nid)
    daysAgo = date_nid.nid_to_days_ago(nid)
    return render(request, 'status.html', {
        'web_domain': web_domain,
        'status': statusTable,
        'date': date,
        'daysAgo': daysAgo,
        'nid': nid,
        'mjd': int(mjd),
        'prettyDate': prettyDate,
#        'lasair_grafana_url': settings.LASAIR_GRAFANA_URL})
        'lasair_grafana_url': 'https://lasair-lsst-dev-svc.lsst.ac.uk/d/iILmd8-Wz/alerts'})    # HACK
