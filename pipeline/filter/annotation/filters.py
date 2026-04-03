import os, sys, time, json, datetime, smtplib

from util import fetch_queries, dispose_query_results

sys.path.append('../../common')
import settings
from src import db_connect, manage_status, date_nid

def annotation_filters(fltr):
    """run_annotation_queries.
    Pulls the recent content from the kafka topic 'lsst_annotations' 
    Each message has an annotator/topic name, and the diaObjectId that was annotated.
    Queries that have that annotator should run against that object
    """

    # how many bytes has each filter already produced
    ms = manage_status.manage_status(msl=fltr.database_remote)
    nid = date_nid.nid_now()

    # first get the user queries from the database that the webserver uses
    #try:
    try:
        query_list = fetch_queries(fltr.database_remote, ms, nid)
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.fetch_queries" + str(e))
    obj_list = fltr.diaObject_ann
    fltr.log.info('fast annotations: ' + str(obj_list))
    ntotal = run_queries(fltr, query_list, ms, nid)
    return ntotal

def run_queries(fltr, query_list, ms, nid):
    ntotal = 0
    for query in query_list:
        n = 0
        t = time.time()
        for ann,objList in fltr.diaObject_ann.items():
            query_results = run_query(query, fltr.database_remote, ann, objList, fltr)
            n += dispose_query_results(query, query_results, fltr, ms, nid)

        t = time.time() - t
        if n > 0:
            fltr.log.info('   %s(%d) got %d in %.1f seconds' % (query['topic_name'], query['active'], n, t))
            sys.stdout.flush()
        ntotal += n
    return ntotal

def query_for_object(query, objList):
    """ modifies an existing query to add a new constraint for a list of objects
    We already know this query comes from multiple tables: objects and annotators,
    so we know there is an existing WHERE clause. Can add the new constraint to the end,
    unless there is an ORDER BY, in which case it comes before that.
    Args:
        query: the original query, as generated from the Lasair query builder
        objList: the object that is the new constraint
    """
    tok = query.replace('order by', 'ORDER BY').split('ORDER BY')
    txtObjList = ','.join([str(id) for id in objList])
    query = tok[0] + ' AND objects.diaObjectId IN (%s) ' % txtObjList
    if len(tok) == 2: # has order clause, add it back
        query += ' ORDER BY ' + tok[1]
    return query

def run_query(query, msl, annotator, objList, fltr):
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
    sqlquery_real = query_for_object(sqlquery_real, objList)
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
        fltr.log.info(error)
        fltr.log.info(sqlquery_real)
        send_email(email, topic, error)
        return []

    return query_results

