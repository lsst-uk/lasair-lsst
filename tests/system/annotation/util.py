""" Test system utilities for annotations
"""
import sys
import time
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import db_connect, annotate_util, topic_name
sys.path.append('../../../webserver/lasair')
from query_builder import build_query

msl        = db_connect.remote()
verbose    = False
sleep_time = 10

def delete_annotator(ann_topic, verbose=False):
    print(f'- Deleting annotator {ann_topic}')
    cursor =  msl.cursor(buffered=True, dictionary=True)

    query = f'DELETE from annotations WHERE topic="{ann_topic}"'
    if verbose: print(query)
    try:
        cursor.execute(query)
    except Exception as e:
        print(str(e))

    query = f'DELETE from annotators WHERE topic="{ann_topic}"'
    if verbose: print(query)
    try:
        cursor.execute(query)
    except Exception as e:
        print(str(e))
    msl.commit()

def delete_filter(filter_name, verbose=False):
    print(f'- Deleting filter {filter_name}')
    query = f'DELETE FROM myqueries where name="{filter_name}"'
    if verbose: print(query)
    cursor =  msl.cursor(buffered=True, dictionary=True)
    try:
        cursor.execute(query)
    except Exception as e:
        print(str(e))
    msl.commit()

def get_userid(username, verbose=False):
    # find user id number for given username
    print(f'- Get userid for username {username}')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    query = f'SELECT id FROM auth_user WHERE username="{username}"'
    if verbose: print(query)
    cursor.execute(query)
    for row in cursor:
        id = row['id']
    if verbose: print(f'- {username} is user number {id}')
    return id

def get_diaObjectId():
    print('- Finding an arbitrary diaObjectId')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    # find an object
    query = f'SELECT diaObjectId FROM objects LIMIT 1'
    if verbose: print(query)
    cursor.execute(query)
    for row in cursor:
        diaObjectId = row['diaObjectId']
    print(f'- diaObjectId is {diaObjectId}')
    return diaObjectId

def make_annotator(topic, username, verbose=False):
    id = get_userid(username)
    print(f'- Making annotator for topic {topic} owned by {username}')
    cursor =  msl.cursor(buffered=True, dictionary=True)
    # make the tags_ annotator
    query = 'INSERT INTO annotators (topic, active, public, user) '
    query += f'VALUES ("{topic}", 1, 0, {id})'
    if verbose: print(query)
    try:
        cursor.execute(query)
    except Exception as e:
        print(str(e))
    msl.commit()

def make_filter_ann(filter_name, username, ann_topic):
    id = get_userid(username)
    tn = topic_name.topic_name(id, filter_name)
    selected   = 'objects.diaObjectId'
    tables     = f'objects,annotator:{ann_topic}'
    conditions = ''
    sql = build_query(selected, tables, conditions)
    query = 'INSERT INTO myqueries '
    query += '(user, name, selected, conditions, tables, public, '
    query += 'run, output, byte_quota, topic_name, real_sql) '
    query += f'VALUES ({id}, "{filter_name}", "{selected}", "{conditions}", "{tables}", 0, '
    query += f'{settings.RUN_ANNOTATION}, {settings.OUTPUT_PLAIN}, 10000000, "{tn}", \'{sql}\')'
    print(f'- Making filter {filter_name}, topic name {tn}, uses annotation {ann_topic}')
    if verbose: print(query)
    cursor =  msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    msl.commit()
    return tn
