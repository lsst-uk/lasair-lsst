import sys
from confluent_kafka import Producer, KafkaError
sys.path.append('..')
import settings as lasair_settings

def insert_annotation(diaObjectId, topic, classification,
                      version='', explanation='', classdict='{}', url=''):
    # adds an annotation/tag to the kafka for processing by filter-annotation
    message = {
        'diaObjectId'   : diaObjectId,
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
    producer = Producer(conf)
    topicout = lasair_settings.ANNOTATION_TOPIC
    try:
        s = json.dumps(message)
        producer.produce(topicout, s)
    except Exception as e:
        return 'Kafka production failed: %s\n' % str(e)
    producer.flush()
    return ''

def delete_annotation(diaObjectId, topic, classification=''):
    # deletes an annotation or deletes a tag (annotation with classificaiton)
    try:
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
    except MySQLdb.Error as e:
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
    except MySQLdb.Error as e:
        return "Cannot connect to master database %s\n" % str(e)

    query = 'SELECT classification FROM annotations '
    query += 'WHERE topic="tags_%s" AND diaObjectId=%d'
    query = query % (username, diaObjectId)
    taglist = []
    for row in cursor:
        taglist.append(row['classification'])
    return taglist

def objects_for_tag(username, tag):
    # all objects with given tag
    try:
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
    except MySQLdb.Error as e:
        return "Cannot connect to master database %s\n" % str(e)

    query = 'SELECT diaObjectId FROM annotations '
    query += 'WHERE topic="tags_%s" AND classification="%s"'
    query = query % (username, tag)
    objlist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
