import sys
import json
from confluent_kafka import Producer, KafkaError
sys.path.append('..')
import settings as lasair_settings
import db_connect

def insert_annotation_kafka(diaObjectId, topic, classification,
                      version='', explanation='', classdict='{}', url=''):
    message = {'diaObjectId'   : diaObjectId,
           'topic'         : topic,
           'version'       : version,
           'classification': classification,
           'explanation'   : explanation,
           'classdict'     : classdict,
           'url'           : url,
       }

    conf = {
       'bootstrap.servers': lasair_settings.INTERNAL_KAFKA_PRODUCER,
        'client.id': 'client-1',
    }

    # will we really instantiate the producer for each message?
    producer = Producer(conf)
    topicout = lasair_settings.ANNOTATION_TOPIC
    try:
        s = json.dumps(message)
        producer.produce(topic, s)
    except Exception as e:
        return {'error': "Kafka production failed: %s\n" % e}
    producer.flush()

def insert_annotation_db(diaObjectId, topic, classification,
                      version='', explanation='', classdict='{}', url='', verbose=False):
    # adds an annotation/tag to the database
    try:
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
    except Exception as e:
        return "Cannot connect to master database %s\n" % str(e)

    queryd = 'DELETE FROM annotations WHERE diaObjectId=%d AND topic="%s"'
    queryd = queryd % (diaObjectId,topic)

    # if its tags, we can have multiple per object/topic
    if topic.startswith('tags_'):
        queryd += 'AND classification="%s"' % classification

    queryi = 'INSERT INTO annotations ('
    queryi += 'diaObjectId, topic, version, classification, explanation, classdict, url'
    queryi += ') VALUES ('
    queryi += "'%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    queryi = queryi % (diaObjectId, topic, version, classification,
        explanation, classdict, url)

    if verbose: print(queryd)
    cursor.execute(queryd)
    if verbose: print(queryi)
    cursor.execute(queryi)

def delete_annotation(diaObjectId, topic, classification='', verbose=False):
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
    
    if verbose: print(query)
    try:
        cursor.execute(query)
    except Exception as e:
        return "Cannot delete annotation: %s" % str(e)

def tags_for_object(username, diaObjectId, verbose=False):
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
    if verbose: print(query)
    taglist = []
    for row in cursor:
        taglist.append(row['classification'])
    return taglist

def objects_for_tag(username, tag, verbose=False):
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
    if verbose: print(query)
    objlist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
    return objlist
