from lasair.utils import mjd_from_iso
import time
import math
import dateutil.parser as dp
import json
from subprocess import Popen, PIPE
from src import date_nid
import settings
from django.db import connection
from django.template.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import sys
sys.path.append('../../../common')


def gw_map_detail(request, skymap_id_version):
    """*return details of the mma_gw map*

    **Key Arguments:**

    - `request` -- the original request
    - `skymap_id_version` -- UUID of the mma_gw map

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('gw_maps/<skymap_id_version>/', views.gw_map_detail, name='gw_map_detail'),
        ...
    ]
    ```           
    """
    json_text = open("/mnt/lasair-head-data/ztf/skymap/%s.json" % skymap_id_version).read()
    skymap_data = json.loads(json_text)
    isodate = skymap_data['meta']['DATE-OBS']
    maxRA = skymap_data['meta']['apointRA']
    maxDE = skymap_data['meta']['apointDec']
    classification = {'BNS': 0, 'NSBH': 0, 'BBH': 0, 'MassGap': 0}

    try:
        classification['BNS'] = int(100 * float(skymap_data['meta']['classification']['BNS']))
    except:
        pass

    try:
        classification['BBH'] = int(100 * float(skymap_data['meta']['classification']['BBH']))
    except:
        pass

    try:
        classification['NSBH'] = int(100 * float(skymap_data['meta']['classification']['NSBH']))
    except:
        pass

    try:
        classification['MassGap'] = int(100 * float(skymap_data['meta']['classification']['MassGap']))
    except:
        pass

    try:
        classification['Terrestrial'] = int(100 * float(skymap_data['meta']['classification']['Terrestrial']))
    except:
        pass

    skymap_distance = 'unknown'
    if 'DISTMEAN' in skymap_data['meta']:
        skymap_distance = '%.1f &plusmn %.1f Mpc' % (float(skymap_data['meta']['DISTMEAN']), float(skymap_data['meta']['DISTSTD']))
    niddate1 = niddate2 = isodate.split('T')[0].replace('-', '')
    tilelist = skymap_data['meta']['histogram']
    mjd = mjd_from_iso(isodate)
    jd1delta = -1.0
    jd2delta = 1.0
    ztf_wanted = coverage_wanted = False
    galaxies_wanted = True

    if request.method == 'POST':
        ztf_wanted = (request.POST.get('ztf_wanted', 'off') == 'on')
        jd1delta = float(request.POST['jd1delta'])
        jd2delta = float(request.POST['jd2delta'])
        coverage_wanted = (request.POST.get('coverage_wanted', 'off') == 'on')
        niddate1 = request.POST['niddate1']
        niddate2 = request.POST['niddate2']
        galaxies_wanted = (request.POST.get('galaxies_wanted', 'off') == 'on')

    nid1 = date_nid.date_to_nid(niddate1)
    nid2 = date_nid.date_to_nid(niddate2)

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)

# ZTF candidates
    ztf_data = []
    ztfquery = "SELECT objectId,jd,ra,decl,fid,magpsf "
    ztfquery += "FROM candidates WHERE jd BETWEEN %f and %f AND \n(" % (mjd + jd1delta, mjd + jd2delta)
    constraint_list = []
    for tile in tilelist:
        constraint = "(ra BETWEEN %.1f and %.1f AND decl BETWEEN %.1f AND %.1f)\n"
        constraint = constraint % (5 * tile[0], 5 * tile[0] + 5, 90 - 5 * tile[1] - 5, 90 - 5 * tile[1])
        constraint_list.append(constraint)
    ztfquery += " OR ".join(constraint_list) + ") ORDER BY objectId"

    if ztf_wanted:
        cursor.execute(ztfquery)
        for row in cursor:
            ztf_data.append({
                'objectId': row['objectId'],
                'jd': row['jd'],
                'ra': row['ra'],
                'dec': row['decl'],
                'fid': row['fid'],
                'magpsf': row['magpsf'],
            })

# Coverage
    coverage = []
    if coverage_wanted:
        query = "SELECT field,fid,ra,decl,SUM(n) as sum "
        query += "FROM coverage WHERE nid BETWEEN %d and %d GROUP BY field,fid,ra,decl" % (nid1, nid2)

        cursor.execute(query)
        for row in cursor:
            coverage.append({
                'field': row['field'],
                'fid': row['fid'],
                'ra': row['ra'],
                'dec': row['decl'],
                'n': int(row['sum'])})
    tok = skymap_id_version.split('_')
    return render(request, 'mma_gw/multimessenger_map_detail.html',
                  {'skymap_id': tok[0], 'skymap_id_version': skymap_id_version, 'isodate': isodate,
                   'niddate1': niddate1, 'niddate2': niddate2,
                   'skymap_distance': skymap_distance,
                   'jd': jd, 'jd1delta': jd1delta, 'jd2delta': jd2delta,
                   'classification': classification,
                   'maxRA': maxRA, 'maxDE': maxDE,
                   'coverage_wanted': coverage_wanted,
                   'coverage': json.dumps(coverage),
                   'ztf_wanted': ztf_wanted,
                   'ztfquery': ztfquery,
                   'nztf': len(ztf_data), 'ztf_data': json.dumps(ztf_data),
                   'galaxies_wanted': galaxies_wanted})


def gw_map_index(request):
    """*return a list of all multimessenger maps*

    **Key Arguments:**

    - `request` -- the original request

    **Usage:**

    ```python
    urlpatterns = [
        ...
        path('gw_maps/', views.gw_map_index, name='gw_map_index'),
        ...
    ]
    ```           
    """
    message = ''
    p = Popen(['ls', '-lrt', '/mnt/cephfs-head-data/ztf/skymap/'], stdout=PIPE)
    skymap_list = []
    result = p.communicate()[0].decode("utf-8")
    for line in result.split('\n'):
        tok = line.split()
        if len(tok) > 7:
            name = tok[8]
            t = name.split('.')
            if len(t) > 1 and t[1] == 'json':
                skymap_list.append(t[0])
    return render(request, 'mma_gw/multimessenger_map_index.html', {'skymap_list': skymap_list, 'message': message})
