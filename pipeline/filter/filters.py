""" Runs the user's queries. 
Fetch them from database, construct SQL, execute, produce kafka

(1) fetch_queries(fltr.remote, ms, nid) 
gets all the queries from the remote database. ms is manage_status and nid is today.

(2) run_queries(batch, query_list, ms, nid):
Uses query_list runs all the queries against local database

(3) run_query(query, msl)
Run a specific query and return query_results

(4) dispose_query_results(query, query_results, fltr, ms, nid)
Deal with the query results

(4a) fetch_digest(topic_name):
    Get the digest file from shared storage

(4b) dispose_email(fltr, allrecords, last_email, query):
    Deal with outgoing emails, it calls this to actually send
    send_email(email, topic, message, message_html):

(4c) dispose_kafka(query_results, query, ms, nid):
    Produce Kafka output to public stream

(4d) write_digest(allrecords, topic_name, last_email):
    Write the digest file for this topic

"""

import os, sys, time, json, datetime, smtplib
from confluent_kafka import Consumer, Producer, KafkaError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append('../../common')
import settings
from src import db_connect, manage_status, date_nid


def fetch_queries(msl_remote, ms, nid):
    """fetch_queries.
    Get all the stored queries from the main database
    """

    # Fetch all the stored queries from the main database
    cursor = msl_remote.cursor(buffered=True, dictionary=True)
    query = 'SELECT mq_id, user, name, email, tables, active, byte_quota, real_sql, topic_name '
    query += 'FROM myqueries, auth_user WHERE myqueries.user = auth_user.id AND active > 0'
    cursor.execute(query)

    query_list = []
    for query in cursor:
        query_dict = {
            'mq_id':     query['mq_id'],
            'user':      query['user'],
            'name':      query['name'],
            'active':    query['active'],
            'email':     query['email'],
            'tables':    query['tables'],
            'real_sql':  query['real_sql'],
            'topic_name':query['topic_name'],
            'byte_quota':query['byte_quota'],
        }
        # Lets see if some kafka has produced on this filter
        nbytesname = query['topic_name'] + '_bytes_produced'
        status = ms.read(nid)
        if nbytesname in status:
            query_dict['bytes_produced'] = status[nbytesname]

        query_list.append(query_dict)
    return query_list

def run_queries(fltr, query_list, ms, nid, annotation_list=None):
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
        if annotation_list is None:
            msl = db_connect.local()
            query_results = run_query(query, fltr.database_local)
            n += dispose_query_results(query, query_results, fltr, ms, nid)
        else:
            for ann in annotation_list:
                query_results = run_query(query, fltr.database_remote,
                   ann['annotator'], ann['diaObjectId'], fltr=fltr)
                n += dispose_query_results(query, query_results, fltr, ms, nid)

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

def run_query(query, msl, annotator=None, diaObjectId=None, fltr=None):
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
    if annotator:
        # if the annotator does not appear in the query tables, then we don't need to run it
        if annotator not in query['tables']:
            return []
        # run the query against main for this specific object that has been annotated
        sqlquery_real = query_for_object(sqlquery_real, diaObjectId)
#        fltr.log.info('FAnnQ: ' + sqlquery_real)

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

def lightcurve_lite(alert):
    attrList = ['psfFlux', 'psfFluxErr', 'midpointMjdTai', 'band', 'reliability']
    diaSourcesList = []
    for ds in alert['diaSourcesList']:
        diaSource = {}
        for attr in attrList:
            diaSource[attr] = ds[attr]
        diaSourcesList.append(diaSource)

    attrList = ['psfFlux', 'psfFluxErr', 'midpointMjdTai', 'band']
    diaForcedSourcesList = []
    for dfs in alert['diaForcedSourcesList']:
        diaForcedSource = {}
        for attr in attrList:
            diaForcedSource[attr] = dfs[attr]
        diaForcedSourcesList.append(diaForcedSource)

    return {
        "diaSourcesList": diaSourcesList,
        "diaForcedSourcesList": diaForcedSourcesList,
    }

def dispose_query_results(query, query_results, fltr, ms, nid):
    """ Send out the query results by email or kafka, and ipdate the digest file
    """
    if len(query_results) == 0:
        return 0
    active = query['active']

    if active == 1:
        # send results by email if 24 hours has passed, returns time of last email send
        digest, last_entry, last_email = fetch_digest(query['topic_name'])
        allrecords = (query_results + digest)[:10000]
        if fltr.send_email:
            last_email = dispose_email(fltr, allrecords, last_email, query)
        utcnow = datetime.datetime.now(datetime.UTC)
        write_digest(allrecords, query['topic_name'], utcnow, last_email)

    # send results by kafka on given topic
    BASIC_KAFKA     = 2
    LIGHTCURVE_LITE = 3
    LIGHTCURVE_FULL = 4
    if not fltr.send_kafka or active < BASIC_KAFKA:
        return len(query_results)

    # try to append the lightcurve info
    if active >= LIGHTCURVE_LITE:
        for q in query_results:
            if 'diaObjectId' in q:
                diaObjectId = q['diaObjectId']
                # see if its in the cache of this batch
                alert = None
                if diaObjectId in fltr.alert_dict:
                    alert = fltr.alert_dict[diaObjectId]
                else:
                    # try to fetch it from cassandra, not yet implemented!
                    fltr.log.info('Cannot find lightcurve {diaObjectId} in alert cache')

                if alert:
                    if active == LIGHTCURVE_LITE:
                        q['alert'] = lightcurve_lite(alert)
                    if active == LIGHTCURVE_FULL:
                        q['alert'] = alert

    dispose_kafka(fltr.producer, query_results, query, ms, nid)
    return len(query_results)

def write_digest(allrecords, topic_name, last_entry, last_email):
    # update the digest file
    last_email_text = last_email.strftime("%Y-%m-%d %H:%M:%S")
    last_entry_text = last_entry.strftime("%Y-%m-%d %H:%M:%S")
    digest_dict = {
            'last_entry': last_entry_text, 
            'last_email': last_email_text, 
            'digest': allrecords
            }
    digestdict_text = json.dumps(digest_dict, indent=2, default=crap_converter)

    filename = settings.KAFKA_STREAMS + '/' + topic_name
    f = open(filename, 'w')
    os.chmod(filename, 0O666)
    f.write(digestdict_text)
    f.close()

def tutc(s):
    return datetime.datetime.strptime(s+' +0000', "%Y-%m-%d %H:%M:%S %z")

def fetch_digest(topic_name):
    filename = settings.KAFKA_STREAMS + '/' + topic_name
    try:
        digest_file = open(filename, 'r')
        digest_dict = json.loads(digest_file.read())
        digest = digest_dict['digest']
        last_entry_text = digest_dict['last_entry']
        last_email_text = digest_dict['last_email']
        digest_file.close()
    except:
        digest = []
        last_entry_text = "2017-01-01 00:00:00"
        last_email_text = "2017-01-01 00:00:00"
    last_entry = tutc(last_entry_text)
    last_email = tutc(last_email_text)
    return digest, last_entry, last_email


def dispose_email(fltr, allrecords, last_email, query, force=False):
    """ Send out email notifications
    """
    utcnow = datetime.datetime.now(datetime.UTC)
    if not force:
        delta = (utcnow - last_email)
        delta = delta.days + delta.seconds/86400.0
        # send a message at most every 24 hours
        # delta is number of days since last email went out
        if delta < 1.0:
            return last_email
    fltr.log.info('   --- send email to %s' % query['email'])
    topic = query['topic_name']
    sys.stdout.flush()
    query_url = '/query/%d/' % (query['mq_id'])
    message = 'Your active query with Lasair on topic %s\n' % topic
    message_html = 'Your active query with Lasair on <a href=%s>%s</a><br/>' % (query_url, topic)
    for out in allrecords: 
        out_time = tutc(out['UTC'])
        # gather all records that have accumulated since last email
        if force or out_time > last_email:
            if 'diaObjectId' in out:
                diaObjectId = str(out['diaObjectId'])
                message += diaObjectId + '\n'
                message_html += '<a href="%s/objects/%s/">%s</a><br/> \n' % (settings.LASAIR_URL, diaObjectId, diaObjectId)
            else:
                jsonout = json.dumps(out, default=crap_converter)
                message += jsonout + '\n'
    try:
        send_email(query['email'], topic, message, message_html)
        return utcnow
    except Exception as e:
        print('ERROR in filter/run_active_queries: Cannot send email!' + str(e))
        print(e)
        sys.stdout.flush()
        return last_email


def send_email(email, topic, message, message_html=''):
    """send_email.

    Args:
        email:
        topic:
        message:
        message_html:
    """
    msg = MIMEMultipart('alternative')

    msg['Subject'] = 'Lasair query ' + topic
    msg['From'] = settings.LASAIR_EMAIL
    msg['To'] = email

    msg.attach(MIMEText(message, 'plain'))
    if len(message_html) > 0:
        msg.attach(MIMEText(message_html, 'html'))
    s = smtplib.SMTP('localhost')
    s.sendmail(settings.LASAIR_EMAIL, email, msg.as_string())
    s.quit()


def dispose_kafka(producer, query_results, query, ms, nid):
    """ Send out query results by kafka to the given topic.
    """
    topic_name = query['topic_name']
    # First decide if this filter has already produced enough
    bp = query.get('bytes_produced', 0)
    bq = query['byte_quota']
    will_produce = (bp < bq) or (bq == 0)

    nbytes = 0
    nalert = 0
    try:
        for out in query_results: 
            if 'alert' in out:
                out['alert'].pop('annotations', None)   # extra Lasair stuff
            jsonout = json.dumps(out, default=crap_converter)
            nbytes += len(jsonout)
            nalert += 1
            if will_produce:
                producer.produce(topic_name, value=jsonout, callback=kafka_ack)
        producer.flush(10.0)   # 10 second timeout
    except Exception as e:
        rtxt = "ERROR in filter/run_active_queries: cannot produce to public kafka"
        rtxt += str(e)
        slack_webhook.send(settings.SLACK_URL, rtxt)
        print(rtxt)
        sys.stdout.flush()

    # Record this as produced or rejected
    if will_produce:
        ms.add({
            topic_name+'_bytes_produced' : nbytes,
            topic_name+'_alerts_produced': nalert,
        }, nid)
    else:
        ms.add({
            topic_name+'_bytes_rejected' : nbytes,
            topic_name+'_alerts_rejected': nalert,
        }, nid)

def crap_converter(o):
    """crap_converter. Deal with the things that JSON can't encode.

    Args:
        o:
    """
# used by json encoder when it gets a type it doesn't understand
    if isinstance(o, datetime.datetime) or type(o).__module__ == 'numpy':
        return o.__str__()
    else:
        return 'Unexpected type in json.dumps:' + str(type(o))

def kafka_ack(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))


def filters(fltr):
    # how many bytes has each filter already produced
    ms = manage_status.manage_status(msl=fltr.database_remote)
    nid = date_nid.nid_now()

    try:
        query_list = fetch_queries(fltr.database_remote, ms, nid)
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.fetch_queries" + str(e))
        return None

    ntotal = run_queries(fltr, query_list, ms=ms, nid=nid)
    return ntotal

def fast_anotation_filters(fltr):
    """run_annotation_queries.
    Pulls the recent content from the kafka topic 'lsst_annotations' 
    Each message has an annotator/topic name, and the diaObjectId that was annotated.
    Queries that have that annotator should run against that object
    """

    # how many bytes has each filter already produced
    ms = manage_status.manage_status(msl=fltr.database_remote)
    nid = date_nid.nid_now()

    # first get the user queries from the database that the webserver uses
    try:
        query_list = fetch_queries(fltr.database_remote, ms, nid)
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
    ntotal = run_queries(fltr, query_list, ms, nid, annotation_list)
    return ntotal

# if __name__ == "__main__":
#     from src import slack_webhook
#     print('--------- RUN ACTIVE FILTERS -----------')
#     sys.stdout.flush()
#     t = time.time()
#     query_list = fetch_queries()
#     run_queries(batch, query_list)
#     print('Active queries done in %.1f seconds' % (time.time() - t))
#     sys.stdout.flush()
