""" Annotation utilities.

Functions for manipulating tags and annotations. Any errors will raise an appropriate exception.
"""
import sys
import json
from confluent_kafka import Producer
sys.path.append('..')
import settings as lasair_settings
sys.path.append('../common/src')
import db_connect


class AnnotationError(Exception):
    """Failure handling an annotation operation."""
    pass


def insert_annotations_kafka(annotations: [{}]):
    """Insert a batch of annotations to the Kafka queue.

    Args:
        annotations: a list of dicts, each having the following fields:
            diaObjectId, topic, classification,[version],[explanation],[classdict],[url]

    Raises:
        KafkaError: error producing to Kafka
    """
    conf = {
        'bootstrap.servers': lasair_settings.INTERNAL_KAFKA_PRODUCER,
        'client.id': 'client-1',
    }

    topicout = lasair_settings.ANNOTATION_TOPIC

    producer = Producer(conf)

    # Set default values if necessary
    for annotation in annotations:
        if 'version' not in annotation:
            annotation['version'] = ''
        if 'explanation' not in annotation:
            annotation['explanation'] = ''
        if 'classdict' not in annotation:
            annotation['classdict'] = '{}'
        if 'url' not in annotation:
            annotation['url'] = ''
        s = json.dumps(annotation)
        producer.produce(topicout, s)

    producer.flush()


def insert_annotation_kafka(diaObjectId: int, topic: str, classification: str,
                            version: str = '', explanation: str = '', classdict: str = '{}', url: str = ''):
    """Insert a single annotation to the Kafka queue. The webserver uses this.

    Raises:
        KafkaError: error producing to Kafka
    """
    insert_annotations_kafka([{
        'diaObjectId': diaObjectId,
        'topic': topic,
        'classification': classification,
        'version': version,
        'explanation': explanation,
        'classdict': classdict,
        'url': url,
    }])


def insert_annotation_db(diaObjectId: int, topic: str, classification: str,
                         version: str = '', explanation: str = '', classdict: str = '{}', url: str = '',
                         verbose: bool = False):
    """Insert an annotation/tag directly to the database

    Args:
        verbose: print the SQL queries on stdout

    Raises:
        mysql.connector.errors.Error: database error
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    queryd = 'DELETE FROM annotations WHERE diaObjectId=%s AND topic=%s'
    paramsd = [diaObjectId, topic]

    # if its tags, we can have multiple per object/topic
    if topic.startswith('tags_'):
        queryd += ' AND classification=%s'
        paramsd.append(classification)

    queryi = 'INSERT INTO annotations ('
    queryi += 'diaObjectId, topic, version, classification, explanation, classdict, url'
    queryi += ') VALUES (%s, %s, %s, %s, %s, %s, %s)'
    paramsi = (diaObjectId, topic, version, classification, explanation, classdict, url)

    if verbose: print(queryd, paramsd)
    cursor.execute(queryd, tuple(paramsd))
    if verbose: print(queryi, paramsi)
    cursor.execute(queryi, paramsi)
    msl.commit()
    msl.close()


def delete_annotation(diaObjectId: int, topic: str, classification: str = None, verbose=False):
    """Deletes an annotation or tag (annotation with classificaiton).

    Args:
        verbose: print the SQL queries on stdout

    Raises:
        mysql.connector.errors.Error: database error
        AnnotationError: an error not caused by anything external
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = 'DELETE FROM annotations WHERE diaObjectId=%s AND topic=%s'
    params = [diaObjectId, topic]

    if topic.startswith('tags_'):
        if classification:
            query += ' AND classification=%s'
            params.append(classification)
        else:
            raise AnnotationError("Cannot delete a tag without a classification")

    if verbose: print(query, params)
    cursor.execute(query, tuple(params))
    msl.commit()
    msl.close()


def classifications_for_object(topic: str, diaObjectId: int, verbose: bool = False) -> list:
    """Fetch all tags connected to an object.

    Args:
        verbose: print the SQL queries on stdout

    Raises:
        mysql.connector.errors.Error: database error

    Returns:
        A list of tags
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = 'SELECT classification FROM annotations '
    query += 'WHERE topic=%s AND diaObjectId=%s'
    if verbose: print(query, (topic, diaObjectId))
    cursor.execute(query, (topic, diaObjectId))
    taglist = []
    for row in cursor:
        taglist.append(row['classification'])
    msl.close()
    return taglist


def objects_for_classification(topic: str, tag: str, verbose: bool = False) -> list:
    """Fetch all objects with given tag.

    Args:
        verbose: print the SQL queries on stdout

    Raises:
        mysql.connector.errors.Error: database error

    Returns:
        A list of objects
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = 'SELECT diaObjectId FROM annotations '
    query += 'WHERE topic=%s AND classification=%s'
    if verbose: print(query, (topic, tag))
    cursor.execute(query, (topic, tag))
    objlist = []
    for row in cursor:
        objlist.append(row['diaObjectId'])
    msl.close()
    return objlist
