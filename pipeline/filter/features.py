""" Computes features of the light curve and builds and object record
"""
from __future__ import print_function
import json
import sys
import math
import numpy as np
import ephem
sys.path.append('../../common/schema/lasair_schema')
from features.FeatureGroup import FeatureGroup

def create_insert_query(alert):
    """create_insert_query.
    Creates an insert sql statement for building the object and 
    a query for inserting it.

    Args:
        alert:
    """

    verbose = False
    lasair_features = FeatureGroup.run_all(alert, verbose)
    if not lasair_features:
        return None
    if verbose:
        print(lasair_features)

    # Make the query
    list = []
    query = 'REPLACE INTO objects SET '
    for key,value in lasair_features.items():
        if not value:
            list.append(key + '= NULL')
        elif math.isnan(value):
            list.append(key + '= NULL')
        elif isinstance(value, str):
            list.append(key + '= "' + str(value) + '"')
        else:
            list.append(key + '=' + str(value))
    query += ',\n'.join(list)
    if verbose:
        print(query)
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
