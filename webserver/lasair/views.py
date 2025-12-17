from lasair.apps.db_schema.utils import get_schema, get_schema_dict, get_schema_for_query_selected
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.conf import settings
import src.date_nid as date_nid
from src import db_connect
import settings as lasair_settings
import importlib
import random
import time
import math
import string
import json
import os
import re
import sys

sys.path.append('../common')


def flux2mag(flux):   # nanoJansky to Magnitude
    if flux > 0:
        mag = 31.4 - 2.5 * math.log10(flux)
        return mag


def index(request):
    """
    Get the most recent events siutable for display on front page.
    The events are grouped by class and age into sets that will all be the same 
    colour and size, for example iclass=0 means SN and iage=2 means age between 2 and 5 days.
    Note that age is time since the most recent alert.
    """
    sherlock_classes = ['SN', 'NT', 'CV', 'AGN']
    base_colors = ['dc322f', '268bd2', '2aa198', 'b58900']

    query = """
    SELECT objects.diaObjectId,
       mjdnow()-objects.lastDiaSourceMjdTai AS "days ago",
       sherlock_classifications.classification AS "predicted type",
       objects.nDiaSources,
       objects.absMag,
       objects.u_psfFlux,
       objects.g_psfFlux,
       objects.r_psfFlux,
       objects.i_psfFlux,
       objects.z_psfFlux,
       objects.y_psfFlux,
       objects.ra, objects.decl
    FROM objects, sherlock_classifications
    WHERE objects.diaObjectId=sherlock_classifications.diaObjectId
       AND objects.nDiaSources > 8
       AND sherlock_classifications.classification in (%s)
    ORDER BY objects.lastDiaSourceMjdTai DESC LIMIT 1000
    """
    S = ['"' + sherlock_class + '"' for sherlock_class in sherlock_classes]
    query = query % (','.join(S))

    table = None
    try:
        # if there is a young cache file, try to use it
        age = time.time() - os.stat(settings.FRONT_PAGE_CACHE).st_mtime
        if age < settings.FRONT_PAGE_STALE:
            f = open(settings.FRONT_PAGE_CACHE, 'r')
            table = json.loads(f.read())
            f.close()
    except:
        pass

    if table is None:
        msl = db_connect.readonly()
        cursor = msl.cursor(buffered=True, dictionary=True)
        cursor.execute(query)

        table = cursor.fetchall()
        # try to write a cache file
        try:
            f = open(settings.FRONT_PAGE_CACHE, 'w')
            f.write(json.dumps(table, indent=2))
            f.close()
        except:
            pass

    nclass = len(sherlock_classes)
    nage = 5

    # 2D array of colors by class and age
    colors = [[] for iclass in range(nclass)]
    for iclass in range(nclass):
        for iage in range(nage):
            r = int(int(base_colors[iclass][0:2], 16) * (0.8 ** iage))
            g = int(int(base_colors[iclass][2:4], 16) * (0.8 ** iage))
            b = int(int(base_colors[iclass][4:6], 16) * (0.8 ** iage))
            colors[iclass].append('#%06x' % (256 * (256 * r + g) + b))

    # 2D array of alerts by class and age
    alerts = [[] for iclass in range(nclass)]
    for iclass in range(nclass):
        alerts[iclass] = [[] for iage in range(nage)]

    for row in table:
        flux = 1
        for fluxband in ['u_psfFlux', 'g_psfFlux', 'r_psfFlux', 'i_psfFlux', 'z_psfFlux', 'y_psfFlux']:
            if row[fluxband] and row[fluxband] > flux:
                flux = row[fluxband]
        row['psfFlux'] = flux
        mag = flux2mag(flux)

        iclass = sherlock_classes.index(row["predicted type"])

        age = row["days ago"]
        if   age < 1: iage = 0
        elif age < 3: iage = 1
        elif age < 5: iage = 2
        elif age <10: iage = 3
        else:         iage = 4

        alerts[iclass][iage].append({
            'diaObjectId': str(row['diaObjectId']),
            'age': row["days ago"],
            'class': row["predicted type"],
            'mag': mag,
            'coordinates': [row['ra'], row['decl']]
        })

    try:
        # MAKE RELATIVE HOME PATH ABSOLUTE
        from os.path import expanduser
        home = expanduser("~")
        newsfile = open(f'{home}/news.txt')
        news = newsfile.read()
        newsfile.close()
    except:
        news = ''

    schema = {}
    schema['diaObjectId'] = 'Unique ID for this object'
    schema['days ago']    = 'Days since last detection of this object'
    schema['sherlock']    = 'Sherlock classification for this object'
    schema['nDiaSources'] = 'Number of detections of this object'
    schema['psfFlux']     = 'Flux from most recent detection in nJ '
    schema['absMag']      = 'Peak absolute magnitude, if known'

    textTable = []
    for t in table:
        textTable.append({
            'diaObjectId'    : t['diaObjectId'],
            'days ago'       : '%.1f' % t['days ago'],
            'sherlock'       : t['predicted type'],
            'nDiaSources'    : t['nDiaSources'],
            'psfFlux'        : '%.0f' % t['psfFlux'],
            'absMag'         : '%.1f'%t['absMag'] if t['absMag'] else '',
        })

    context = {
        'web_domain': lasair_settings.WEB_DOMAIN,
        'alerts': str(alerts),
        'colors': str(colors),
        'news': news,
        'table': textTable,
        'schema': schema,
    }
    return render(request, 'index.html', context)
