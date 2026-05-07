import os, sys, time, json, datetime

# some help from upstairs
from util import fetch_queries, dispose_query_results

sys.path.append('../../common')
import settings


def annotation_filters(fltr):
    """run_annotation_queries.
    Pulls the recent content from the kafka topic 'lsst_annotations' 
    Each message has an annotator/topic name, and the diaObjectId that was annotated.
    Queries that have that annotator should run against that object
    """

    # first get the user queries from the database that the webserver uses
    try:
        query_list = fetch_queries(fltr)
    except Exception as e:
        fltr.log.error("ERROR: " + str(e))
        return 0
    msg = ''
    for topic, ann_list in fltr.ann_diaObjectId.items():
        if len(ann_list) > 5:
            msg += '%s --> %s ...\n' % (topic, ann_list[:5])
        else:
            msg += '%s --> %s\n' % (topic, ann_list)
    fltr.log.info('annotated objects: ' + msg)

    ntotal = run_queries(fltr, query_list)
    return ntotal


def run_queries(fltr, query_list):
    """
    Run all the queries (set to run on annotation or both) against the local database
    """
    ntotal = 0
    for query in query_list:
        if query['run'] == settings.RUN_ANNOTATION 
        or query['run'] == settings.RUN_BOTH:
            n = 0
            t = time.time()
            for ann, objList in fltr.ann_diaObjectId.items():
                query_results = run_query(query, fltr.database_remote, ann, objList, fltr)
                n += dispose_query_results(fltr, query, query_results)

            t = time.time() - t
            if n > 0:
                fltr.log.info('   %s(%d) got %d in %.1f seconds' % (query['topic_name'], query['output'], n, t))
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


def append_lightcurve(fltr, query_results):
    """ fetch the full lightcurve from cassandra if wanted
        put it into the lightcurve cache fltr.message_dict
        that will be further processed in the dispose_kafka method in ../util.py
    """
    for q in query_results:
        diaObjectId = q['diaObjectId']
        # don't fetch if we already have it
        if diaObjectId in fltr.message_dict:
            continue

        (diaObject, diaSourcesList, diaForcedSourcesList) = \
            fltr.lightcurve.fetch(diaObjectId, lite=False)

        fltr.message_dict[diaObjectId] = {
            'diaObjectId':diaObjectId,
            'diaObject':diaObject,
            'diaSourcesList':diaSourcesList,
            'diaForcedSourcesList':diaForcedSourcesList}


def run_query(query, msl, annotator, objList, fltr):
    """run_query. 
        checks if the query involves the annotator,
        and if so, runs the query for the given object on main database
        runs the query against the remote database

    Args:
        query:
        msl:
    """
    output = query['output']
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

    # in any case, 10 second timeout and limit the output
    sqlquery_real = ('SET STATEMENT max_statement_time=%d FOR %s LIMIT %d' %
                     (settings.MAX_STATEMENT_TIME, sqlquery_real, limit))

    cursor = msl.cursor(buffered=True, dictionary=True)
    query_results = []
    utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(sqlquery_real)
        for record in cursor:
            recorddict = dict(record)
            recorddict['UTC'] = utc
            query_results.append(recorddict)
    except Exception as e:
        error = ("%s UTC: Your streaming query %s didn't run, the error is: %s, please check it,"
                 "and write to lasair-help@mlist.is.ed.ac.uk if you want help." % (utc, topic, str(e)))
        fltr.log.info(error)
        fltr.log.info(sqlquery_real)
        send_email(email, topic, error)
        return []

    # fetch the lite or full lightcurve from cassandra if wanted
    if output >= settings.OUTPUT_LITE:   # a lightcurve is needed
        append_lightcurve(fltr, query_results)

    return query_results
