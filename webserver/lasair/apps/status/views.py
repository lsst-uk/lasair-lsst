import json
from django.shortcuts import render
import src.date_nid as date_nid
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
    try:
        filename = '%s_%d.json' % (settings.SYSTEM_STATUS, nid)
        jsonstr = open(filename).read()
    except:
        jsonstr = ''

    try:
        status = json.loads(jsonstr)
    except:
        status = None

    if status and 'today_filter' in status:
        status['today_singleton'] = \
            status['today_filter'] - status['today_filter_out'] - status['today_filter_ss']

    # KEY: (DEFINITION, COMMENT)
    statusSchema = {
        'today_alert': ('Alerts received by Ingest stage today', ''),
        'today_candidate': ('New detections today', ''),
        'update_time': ('Last Lasair update time (UTC)', ''),
        'today_filter': ('Alerts received by Filter stage today', 'Database Alerts + Solar System Alerts'),
        'today_filter_out': ('Alerts sent to database today', ''),
        'today_filter_ss': ('Solar system detections today', ''),
        'today_ztf': ('Alerts sent by ZTF today', ''),
        'today_database': ('Updated objects in database today', ''),
        'total_count': ("Total objects in database", ''),
        'min_delay': ('Hours since most recent alert', ''),
        'nid': ('Night number (nid)', ''),
        "mjd": ('MJD', ''),
        'countTNS': ('Number in TNS database', ''),
        'today_singleton': ('Singletons today', '')
    }
    statusOrder = ["total_count", "nid", "update_time", "today_ztf", "today_alert", "today_filter_out", "today_filter_ss", "today_filter", "today_candidate", "today_database", "min_delay", "countTNS"]

    for k, v in statusSchema.items():
        if not k in status:
            status[k] = ''

    statusTable = []

    if status:
        statusTable[:] = [(statusSchema[s][0], status[s], statusSchema[s][1]) for s in statusOrder]

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
        'lasair_grafana_url': settings.LASAIR_GRAFANA_URL})
