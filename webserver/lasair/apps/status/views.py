import sys
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

def tostr(f):
    s = int(round(f, 0))
    return f'{s:,}'

def combine_status(status):
    # the keys come in as apple_0=123, apple_1=199 etc from the nodes
    # here we combine them into a list apple = [123,199]
    keys = sorted(status.keys())
    new_status = {}
    for key in keys:
        if not key in status:
            continue
        v = '%.0f' % status[key]
        # collect values from different nodes
        if key.endswith('_0'):
            kl = []
            root = key[:-2]
            for i in range(10):
                other_key = '%s_%d' % (root, i)
                if other_key in status:
                    s = int(status[other_key])
                    kl.append(s)
                    del status[other_key]
                else:
                    new_status[root] = str(kl)
                    break
        else:
            s = tostr(status[key])
            new_status[key] = s
    return new_status

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
    status = combine_status(ms.read(nid))

    statusSchema = {
        'today_alert'      : 'Alerts received today',
        'today_lsst'       : 'Alerts sent by LSST today',
        'diaObject'        : 'NonSS objects received today',
        'nSSObject'         : 'SS objects received today',
        'nSSSource'         : 'SS sources received today',
        'min_delay'        : 'Hours since most recent alert',
        'diaSource'        : 'Detections received',
        'diaSourceDB'      : 'Detections inserted into Cassandra',
        'diaForcedSource'  : 'Forced detections received',
        'diaForcedSourceDB': 'Forced detections inserted into Cassandra',
        'today_filter'     : 'Alerts received by Filter stage today',
        'today_filter_out' : 'Alerts sent to MySQL today',
        'today_database'   : 'Objects with detections today',
        'total_count'      : "Total objects in database",

        'icassandra'       :'icassandra time today, seconds',
        'icutout'          :'icutout time today, seconds',
        'ifuture'          :'ifuture time today, seconds',
        'ikconsume'        :'ikconsume time today, seconds',
        'ikproduce'        :'ikproduce time today, seconds',
        'itotal'           :'ingest total time today, seconds',
        'ffeatures'        :'features time today, seconds',
        'fwatchlist'       :'watchlist time today, seconds',
        'fwatchmap'        :'watchmap time today, seconds',
        'fmmagw'           :'mmagw time today, seconds',
        'ffilters'         :'filters time today, seconds',
        'ftransfer'        :'transfer time today, seconds',
        'ftotal'           :'total filter time today, seconds',

        'nid'              : 'Night number (nid)',
    }

    statusTable = []
    for k,v in statusSchema.items():
        if k in status:
            statusTable.append((v, status[k]))

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
