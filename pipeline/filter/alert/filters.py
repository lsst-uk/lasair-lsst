import os, sys, time, json, datetime, smtplib
from confluent_kafka import Consumer, Producer, KafkaError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord
from util import fetch_queries, dispose_query_results

import watchlists
import watchmaps
import mmagw

sys.path.append('../../common')
import settings

def filters(fltr):
    try:
        query_list = fetch_queries(fltr)
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.fetch_queries" + str(e))
        return None

    ntotal = run_queries(fltr, query_list)
    return ntotal

def run_queries(fltr, query_list):
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
        query_results = run_query(query, fltr.database_local)
        n += dispose_query_results(fltr, query, query_results)
        t = time.time() - t
        if n > 0:
            fltr.log.info('   %s(%d) got %d in %.1f seconds' % (query['topic_name'], query['active'], n, t))
            sys.stdout.flush()
        ntotal += n
    return ntotal

def run_query(query, msl):
    """run_query. Two cases here:

    Args:
        query:
        msl:
    """
    active = query['active']
    email = query['email']
    topic = query['topic_name']
    limit = 1000
    sqlquery_real = query['real_sql']

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
                 "and write to lasair-help@mlist.is.ed.ac.uk if you want help." % (utc, topic, str(e)))
        print(error)
        print(sqlquery_real)
        send_email(email, topic, error)
        return []

    return query_results

