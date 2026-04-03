import os, sys, time, json, datetime, smtplib
from confluent_kafka import Consumer, Producer, KafkaError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import filters
import watchmaps
import mmagw

sys.path.append('../../common')
import settings
from src import db_connect, manage_status, date_nid

def filters(fltr):
    # how many bytes has each filter already produced
    self.nid = date_nid.nid_now()

    try:
        query_list = fetch_queries(fltr)
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.fetch_queries" + str(e))
        return None

    ntotal = run_queries(fltr, query_list)
    return ntotal

def run_queries(fltr, query_list, annotation_list):
    """
    When annotation_list is None, it runs all the queries against the local database
    When not None, runs some queires agains a specific object, using the main database
    """

#    if annotation_list and len(annotation_list) > 0:
#        fltr.log.info(annotation_list)
    ntotal = 0
    for query in query_list:
        n = 0
        t = time.time()
        for ann in annotation_list:
            query_results = run_query(query, fltr.database_remote,
               ann['annotator'], ann['diaObjectId'], fltr=fltr)
            n += dispose_query_results(fltr, query, query_results)

        t = time.time() - t
        if n > 0:
            fltr.log.info('   %s(%d) got %d in %.1f seconds' % (query['topic_name'], query['active'], n, t))
            sys.stdout.flush()
        ntotal += n
    return ntotal

def query_for_object(query, diaObjectId):
    """ modifies an existing query to add a new constraint for a specific object.
    We already know this query comes from multiple tables: objects and annotators,
    so we know there is an existing WHERE clause. Can add the new constraint to the end,
    unless there is an ORDER BY, in which case it comes before that.
    Args:
        query: the original query, as generated from the Lasair query builder
        diaObjectId: the object that is the new constraint
    """
    tok = query.replace('order by', 'ORDER BY').split('ORDER BY')
    query = tok[0] + (' AND objects.diaObjectId=%s ' % str(diaObjectId))
    if len(tok) == 2: # has order clause, add it back
        query += ' ORDER BY ' + tok[1]
    return query

def run_query(query, msl, annotator, diaObjectId, fltr):
    """run_query. Two cases here:
    if annotator=None, runs the query against the local database
    if annotator and diaObjectId, checks if the query involves the annotator,
        and if so, runs the query for the given object on main database
        runs the query against the local database

    Args:
        query:
        msl:
    """
    active = query['active']
    email = query['email']
    topic = query['topic_name']
    limit = 1000

    sqlquery_real = query['real_sql']

# special way to run query if there are fresh annotations
    # if the annotator does not appear in the query tables, then we don't need to run it
    if annotator not in query['tables']:
        return []
    # run the query against main for this specific object that has been annotated
    sqlquery_real = query_for_object(sqlquery_real, diaObjectId)
#    fltr.log.info('FAnnQ: ' + sqlquery_real)

    # in any case, 10 second timeout and limit the output
    sqlquery_real = ('SET STATEMENT max_statement_time=%d FOR %s LIMIT %d' %
                     (settings.MAX_STATEMENT_TIME, sqlquery_real, limit))

    cursor = msl.cursor(buffered=True, dictionary=True)
    n = 0
    query_results = []
    utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(sqlquery_real)
        for record in cursor:
            recorddict = dict(record)
            recorddict['UTC'] = utc
            query_results.append(recorddict)
            n += 1
    except Exception as e:
        error = ("%s UTC: Your streaming query %s didn't run, the error is: %s, please check it,"
                 "and write to lasair-help@roe.ac.uk if you want help." % (utc, topic, str(e)))
        print(error)
        print(sqlquery_real)
        send_email(email, topic, error)
        return []

    return query_results

def fast_anotation_filters(fltr):
    """run_annotation_queries.
    Pulls the recent content from the kafka topic 'lsst_annotations' 
    Each message has an annotator/topic name, and the diaObjectId that was annotated.
    Queries that have that annotator should run against that object
    """

    # first get the user queries from the database that the webserver uses
    try:
        query_list = fetch_queries(fltr)
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.fetch_queries" + str(e))
        return None

    annotation_list = []
    conf = {
        'bootstrap.servers':   settings.KAFKA_SERVER,
        'group.id':            settings.ANNOTATION_GROUP_ID,
        'default.topic.config': {'auto.offset.reset': 'earliest'}
    }
    streamReader = Consumer(conf)
    topic = settings.ANNOTATION_TOPIC
    streamReader.subscribe([topic])
    while 1:
        msg = streamReader.poll(timeout=5)
        if msg == None: break
        try:
            ann = json.loads(msg.value())
            annotation_list.append(ann)
        except:
            continue
    streamReader.close()
    fltr.log.info('fast annotations: ' + str(annotation_list))
    ntotal = run_queries(fltr, query_list, annotation_list)
    return ntotal
