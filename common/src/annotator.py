import sys
import json
from confluent_kafka import Producer, KafkaError
sys.path.append('..')
import settings as lasair_settings
import db_connect

def insert_annotation(diaObjectId, topic, classification,
                      version='', explanation='', classdict='{}', url=''):
    # adds an annotation/tag to the database
    try:
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
    except Exception as e:
        return "Cannot connect to master database %s\n" % str(e)

    queryd = 'DELETE FROM annotations WHERE diaObjectId=%d AND topic="%s"'
    queryd = queryd % (
            annotation['diaObjectId'],
            annotation['topic'])

    queryi = 'INSERT INTO annotations ('
    queryi += 'diaObjectId, topic, version, classification, explanation, classdict, url'
    queryi += ') VALUES ('
    queryi += "'%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    queryi = queryi % (
            annotation['diaObjectId'],
            annotation['topic'],
            annotation['version'],
            annotation['classification'],
            annotation['explanation'],
            annotation['classdict'],
            annotation['url'])

    # classic annotations have unique classification
    if not topic.startswith('tags_'):
        self.execute_remote_query(queryd)

    # actually insert the annotation
    self.execute_remote_query(queryi)

def delete_annotation(diaObjectId, topic, classification=''):
    # deletes an annotation or deletes a tag (annotation with classificaiton)
    try:
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
    except Exception as e:
        return "Cannot connect to master database %s\n" % str(e)

    query = 'DELETE from annotations WHERE diaObjectId=%d AND topic="%s"'
    query = query % (diaObjectId, topic)

    if topic.startswith('tags_'):
        if len('classification') > 0:
            query += ' AND classification=%s' % classification
        else:
            return "Cannot delete a tag without a classification"
    
    try:
        cursor.execute(query)
    except Exception as e:
        return "Cannot delete annotation: %s" % str(e)

def tags_for_object(username, diaObjectId):
    # all tags connected to an object
    try:
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
    except Exception as e:
        return "Cannot connect to master database %s\n" % str(e)

    query = 'SELECT classification FROM annotations '
    query += 'WHERE topic="tags_%s" AND diaObjectId=%d'
    query = query % (username, diaObjectId)
    cursor.execute(query)
    print(query)
    taglist = []
    for row in cursor:
        taglist.append(row['classification'])
    return taglist

def objects_for_tag(username, tag):
    # all objects with given tag
    try:
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
    except Exception as e:
        return "Cannot connect to master database %s\n" % str(e)

    query = 'SELECT diaObjectId FROM annotations '
    query += 'WHERE topic="tags_%s" AND classification="%s"'
    query = query % (username, tag)
    cursor.execute(query)
    print(query)
    objlist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
    return objlist
