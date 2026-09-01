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
import make_tag_annotator

MARK_FAVOURITE = 'favourite'
MARK_HIDDEN = 'hidden'
MARKS = (MARK_FAVOURITE, MARK_HIDDEN)


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
                         verbose: bool = False, msl=None):
    """Insert an annotation/tag directly to the database

    Args:
        verbose: print the SQL queries on stdout
        msl: an open connection to join an existing transaction. When given,
            the caller owns the commit and the close; when not, this function
            opens, commits and closes its own connection.

    Raises:
        mysql.connector.errors.Error: database error
    """
    caller_owns_connection = msl is not None
    if not caller_owns_connection:
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
    if not caller_owns_connection:
        msl.commit()
        msl.close()


def delete_annotation(diaObjectId: int, topic: str, classification: str = None, verbose=False, msl=None):
    """Deletes an annotation or tag (annotation with classificaiton).

    Args:
        verbose: print the SQL queries on stdout
        msl: an open connection to join an existing transaction. When given,
            the caller owns the commit and the close; when not, this function
            opens, commits and closes its own connection.

    Raises:
        mysql.connector.errors.Error: database error
        AnnotationError: an error not caused by anything external
    """
    caller_owns_connection = msl is not None
    if not caller_owns_connection:
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
    if not caller_owns_connection:
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


def tag_topic(username: str) -> str:
    """The topic of a user's own tag annotator.

    Args:
        username: the user's name

    Returns:
        The annotator topic, `tags_<username>`

    **Usage:**

        topic = annotate_util.tag_topic('dave')
    """
    return 'tags_%s' % username


def mark_object(user, diaObjectId: int, mark: str, verbose: bool = False):
    """Set a user's mark on an object to `favourite`, `hidden` or no mark at all.

    This is the only function that changes a mark. It owns validation, the rule
    that favourite and hidden are mutually exclusive, and both writes, which
    happen in one transaction. The write is synchronous and direct to the
    database, so it does not reach Kafka and does not fire annotation-triggered
    filters.

    Args:
        user: the marking user, carrying `username` and `id`
        diaObjectId: the object being marked
        mark: `'favourite'`, `'hidden'` or `None` to clear whichever is held
        verbose: print the SQL queries on stdout

    Raises:
        AnnotationError: `mark` is not a mark
        mysql.connector.errors.Error: database error

    Returns:
        The mark held before this call, or `None`

    **Usage:**

        previous = annotate_util.mark_object(request.user, 123, 'favourite')
    """
    return mark_objects(user, [diaObjectId], mark, verbose=verbose)[0]['previous']


def mark_objects(user, diaObjectIds: list, mark: str, verbose: bool = False) -> list:
    """Set a user's mark on several objects, all or nothing.

    One connection and one commit however long the list, so a caller that
    batched a set either marks all of it or none of it.

    Args:
        user: the marking user, carrying `username` and `id`
        diaObjectIds: the objects being marked
        mark: `'favourite'`, `'hidden'` or `None` to clear whichever is held
        verbose: print the SQL queries on stdout

    Raises:
        AnnotationError: `mark` is not a mark
        mysql.connector.errors.Error: database error

    Returns:
        A list of `{'diaObjectId', 'mark', 'previous'}`, in the order given

    **Usage:**

        results = annotate_util.mark_objects(request.user, [123, 456], 'hidden')
    """
    if mark is not None and mark not in MARKS:
        raise AnnotationError("Not a mark: %s" % mark)

    topic = tag_topic(user.username)

    msl = db_connect.remote()
    try:
        # THE ANNOTATOR IS PROVISIONED LAZILY, ON THE WRITE PATH ONLY
        make_tag_annotator.make_annotator(msl, user.username, user.id)

        results = []
        for diaObjectId in diaObjectIds:
            held = marks_held(msl, topic, diaObjectId, verbose=verbose)

            # AN OBJECT CAN HOLD BOTH MARKS IF THEY WERE WRITTEN THROUGH /api/annotate/
            previous = None
            if mark in held:
                previous = mark
            elif held:
                previous = held[0]

            if mark:
                insert_annotation_db(diaObjectId, topic, mark, msl=msl, verbose=verbose)
            for classification in held:
                if classification != mark:
                    delete_annotation(diaObjectId, topic, classification,
                                      msl=msl, verbose=verbose)

            results.append({
                'diaObjectId': diaObjectId,
                'mark': mark,
                'previous': previous,
            })

        msl.commit()
    finally:
        msl.close()
    return results


def marks_held(msl, topic: str, diaObjectId: int, verbose: bool = False) -> list:
    """The marks one topic holds on one object, read on an open connection.

    Args:
        msl: an open connection to the main database
        topic: the tag topic to read, `tags_<username>`
        diaObjectId: the object to look up
        verbose: print the SQL query on stdout

    Raises:
        mysql.connector.errors.Error: database error

    Returns:
        A list of the classifications held, empty when there are none
    """
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT classification FROM annotations '
    query += 'WHERE diaObjectId=%s AND topic=%s AND classification IN (%s, %s)'
    params = (diaObjectId, topic, MARK_FAVOURITE, MARK_HIDDEN)
    if verbose: print(query, params)
    cursor.execute(query, params)
    return [row['classification'] for row in cursor]


def marks_for_objects(topic: str, diaObjectIds: list, verbose: bool = False) -> dict:
    """Fetch the favourite and hidden marks one tag topic holds over given objects.

    Bounded by the ids passed in, so it stays cheap however large the user's
    mark set grows. Callers with an unbounded list of ids must chunk it.

    Args:
        topic: the tag topic to read, `tags_<username>`
        diaObjectIds: the objects to look up
        verbose: print the SQL queries on stdout

    Raises:
        mysql.connector.errors.Error: database error

    Returns:
        A dict of `{diaObjectId: 'favourite'|'hidden'}`, holding only the
        objects that carry a mark

    **Usage:**

        marks = annotate_util.marks_for_objects('tags_dave', [123, 456])
    """
    if not diaObjectIds:
        return {}

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    placeholders = ', '.join(['%s'] * len(diaObjectIds))
    query = 'SELECT diaObjectId, classification FROM annotations '
    query += 'WHERE topic=%s AND classification IN (%s, %s) '
    query += 'AND diaObjectId IN (' + placeholders + ')'
    params = (topic, MARK_FAVOURITE, MARK_HIDDEN) + tuple(diaObjectIds)
    if verbose: print(query, params)
    cursor.execute(query, params)

    marks = {}
    for row in cursor:
        marks[row['diaObjectId']] = row['classification']
    msl.close()
    return marks


def delete_classification(topic: str, classification: str, verbose: bool = False) -> int:
    """Delete every row of one mark from a tag topic.

    This is the Hidden page's "Unhide all". Only a mark may be cleared
    wholesale, so a stray call cannot empty a user's hand-written tags.

    Args:
        topic: the tag topic to clear, `tags_<username>`
        classification: `favourite` or `hidden`
        verbose: print the SQL query on stdout

    Raises:
        AnnotationError: `classification` is not a mark
        mysql.connector.errors.Error: database error

    Returns:
        The number of rows deleted

    **Usage:**

        removed = annotate_util.delete_classification('tags_dave', 'hidden')
    """
    if classification not in MARKS:
        raise AnnotationError("Not a mark: %s" % classification)

    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = 'DELETE FROM annotations WHERE topic=%s AND classification=%s'
    params = (topic, classification)
    if verbose: print(query, params)
    cursor.execute(query, params)
    removed = cursor.rowcount
    msl.commit()
    msl.close()
    return removed


def count_classification(topic: str, classification: str, verbose: bool = False) -> int:
    """Count the annotations one topic holds with a given classification.

    Args:
        topic: the topic to count within
        classification: the classification to count
        verbose: print the SQL query on stdout

    Raises:
        mysql.connector.errors.Error: database error

    Returns:
        The number of rows

    **Usage:**

        n = annotate_util.count_classification('tags_dave', 'favourite')
    """
    msl = db_connect.remote()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = 'SELECT COUNT(*) AS n FROM annotations WHERE topic=%s AND classification=%s'
    params = (topic, classification)
    if verbose: print(query, params)
    cursor.execute(query, params)
    row = cursor.fetchone()
    msl.close()
    return row['n'] if row else 0


def count_favouriters(diaObjectId: int, verbose: bool = False) -> int:
    """Count how many users have favourited an object.

    Aggregate only. There is no function, key, endpoint or parameter, now or
    later, that maps an object to the users who favourited it: this is the one
    surface of the feature that crosses the per-user boundary.

    The `tags_` guard is not decorative — without it any third-party annotator
    that happens to emit `classification='favourite'` would be counted as a
    user favourite.

    Args:
        diaObjectId: the object to count for
        verbose: print the SQL query on stdout

    Raises:
        mysql.connector.errors.Error: database error

    Returns:
        The number of users who have favourited the object

    **Usage:**

        n = annotate_util.count_favouriters(123)
    """
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)

    query = 'SELECT COUNT(*) AS n FROM annotations '
    query += "WHERE diaObjectId=%s AND classification=%s AND topic LIKE 'tags\\_%'"
    params = (diaObjectId, MARK_FAVOURITE)
    if verbose: print(query, params)
    cursor.execute(query, params)
    row = cursor.fetchone()
    msl.close()
    return row['n'] if row else 0
