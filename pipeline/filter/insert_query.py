""" Computes features of the light curve and builds and object record
"""
from __future__ import print_function
import json
import sys
import math
import numpy as np
import ephem
from features import create_lasair_features
from gkhtm import _gkhtm as htmCircle

def create_insert_query(alert):
    """create_insert_query.
    Creates an insert sql statement for building the object and 
    a query for inserting it.

    Args:
        alert:
    """
    diaObject = alert['diaObject']

    # Make a list of diaSources
    if 'diaSource' in alert and alert['diaSource'] != None:
        if 'prvDiaSources' in alert and alert['prvDiaSources'] != None:
            diaSourceList = alert['prvDiaSources'] + [alert['diaSource']]
        else:
            diaSourceList = [alert['diaSource']]

    # Make a list of diaForcedSources
    if 'prvrDdiaForcedSources' in alert:
        diaForcedSourceList = alert['prvForcedDiaSources'] + [alert['diaSource']]
    else:
        diaForcedSourceList = []

    # Make a list of diaNondetectionLimits
    if 'prvDiaNondetectionLimits' in alert:
        diaNondetectionLimitsList = alert['prvDiaNondetectionLimits']
    else:
        diaNondetectionLimitsList = []

    lasair_features = create_lasair_features(
            diaObject, 
            diaSourceList, 
            diaForcedSourceList, 
            diaNondetectionLimitsList)

    # Compute the HTM ID for later cone searches
    try:
        htm16 = htmCircle.htmID(16, diaObject['ra'], diaObject['decl'])
    except:
        htm16 = 0
        print('ERROR: filter/insert_query: Cannot compute HTM index')
        sys.stdout.flush()

    sets = {**diaObject, 'htm16':htm16, **lasair_features}

    # Make the query
    list = []
    query = 'REPLACE INTO diaObjects SET '
    for key,value in sets.items():
        print
        if not value:
            list.append(key + '= NULL')
        elif math.isnan(value):
            list.append(key + '= NULL')
        elif isinstance(value, str):
            list.append(key + '= "' + str(value) + '"')
        else:
            list.append(key + '=' + str(value))
    query += ',\n'.join(list)
    return query

def create_insert_annotation(diaObjectId, annClass, ann, attrs, table, replace):
    """create_insert_annotation.
    This code makes the insert query for the genaric annotation

    Args:
        diaObjectId:
        annClass:
        ann:
        attrs:
        table:
        replace:
    """
    sets = {}
    for key in attrs:
        sets[key] = 0
    for key, value in ann.items():
        if key in attrs and value:
            sets[key] = value
    if 'description' in attrs and not 'description' in ann:
        sets['description'] = 'no description'
    # Build the query
    list = []
    if replace: query = 'REPLACE'
    else:       query = 'INSERT'
    query += ' INTO %s SET ' % (table)
    for key,value in sets.items():
        list.append(key + '=' + "'" + str(value).replace("'", '') + "'")
    query += ',\n'.join(list)
    query = query.replace('None', 'NULL')
    return query