""" Runs the user's queries. 
Fetch them from database, construct SQL, execute, produce kafka

(1) fetch_queries(): 
gets all the queries from the database

(2) run_annotation_queries(query_list): 
may be called to get all the recent fast annotations 

(3) run_queries(batch, query_list, annotation_list=None):
Uses query_list and possibly annotation_list and runs all the queries against 
local, or those involving annotator against main databaase

(4) query_for_object(query, diaObjectId):
If doing fast annotations, convert a given query with specific diaObjectId

(5) run_query(query, msl, annotator=None, diaObjectId=None):
Run a specific query and return query_results

(6) dispose_query_results(query, query_results):
Deal with the query results

(6a) fetch_digest(topic_name):
    Get the digest file from shared storage

(6b) dispose_email(allrecords, last_email, query):
    Deal with outgoing emails, it calls this to actually send
    send_email(email, topic, message, message_html):

(6c) dispose_kafka(query_results, topic):
    Produce Kafka output to public stream

(6d) write_digest(allrecords, topic_name, last_email):
    Write the digest file for this topic

"""

import os, sys, time, json, datetime, smtplib
from confluent_kafka import Consumer, Producer, KafkaError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append('../../common')
import settings
from src import db_connect


def fetch_queries():
    """fetch_queries.
    Get all the stored queries from the main database
    """
    # first get the user queries from the database that the webserver uses
    msl_remote = db_connect.remote()

    # Fetch all the stored queries from the main database
    cursor = msl_remote.cursor(buffered=True, dictionary=True)
    query = 'SELECT mq_id, user, name, email, tables, active, real_sql, topic_name '
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
        }
        query_list.append(query_dict)
    return query_list


def run_queries(fltr, query_list, annotation_list=None):
    """
    When annotation_list is None, it runs all the queries against the local database
    When not None, runs some queires agains a specific object, using the main database
    """

    ntotal = 0
    for query in query_list:
        n = 0
        t = time.time()

        # normal case of streaming queries
        if annotation_list is None:
            query_results = run_query(query, fltr.database, fltr=fltr)
            n += dispose_query_results(query, query_results, fltr)

        # immediate response to active=2 annotators
        else:
            for ann in annotation_list:  
                # msl_remote = db_connect.remote()
                query_results = run_query(query, fltr.database,
                                          ann['annotator'], ann['diaObjectId'], fltr=fltr)
                print('fast annotator %s on object %s' % (ann['annotator'], ann['diaObjectId']))
                print('results:', query_results)
                n += dispose_query_results(query, query_results, fltr)

        t = time.time() - t
        if n > 0:
            print('   %s got %d in %.1f seconds' % (query['topic_name'], n, t))
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

    Args:
        query:
        msl:
        fltr:
        diaObjectId:
        annotator:
    """
    active = query['active']
    email = query['email']
    topic = query['topic_name']
    limit = 1000

    sqlquery_real = query['real_sql']
    if annotator:
        # if the annotator does not appear in the query tables, then we don't need to run it
        if query['tables'] not in annotator:
            return []
        # run the query against main for this specific object that has been annotated
        sqlquery_real = query_for_object(sqlquery_real, diaObjectId)

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
            # print(recorddict)
            query_results.append(recorddict)
            n += 1
    except Exception as e:

        error = ("%s UTC: Your streaming query %s didn't run, the error is: %s, please check it,"
                 "and write to lasair-help@roe.ac.uk if you want help." % (utc, topic, str(e)))
        print(error)
        print(sqlquery_real)
        if not fltr or fltr.send_email:
            send_email(email, topic, error)
        return []

    return query_results


def dispose_query_results(query, query_results, fltr=None):
    """ Send out the query results by email or kafka, and ipdate the digest file
    """
    if len(query_results) == 0:
        return 0
    active = query['active']
    digest, last_entry, last_email = fetch_digest(query['topic_name'])
    allrecords = (query_results + digest)[:10000]

    if active == 1:
        # send results by email if 24 hours has passed, returns time of last email send
        if not fltr or fltr.send_email:
            last_email = dispose_email(allrecords, last_email, query)

    if active == 2:
        # send results by kafka on given topic
        if not fltr or fltr.send_kafka:
            dispose_kafka(query_results, query['topic_name'])

    utcnow = datetime.datetime.now(datetime.UTC)
    write_digest(allrecords, query['topic_name'], utcnow, last_email)
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
    digestdict_text = json.dumps(digest_dict, indent=2, default=datetime_converter)

    filename = settings.KAFKA_STREAMS + '/' + topic_name
    f = open(filename, 'w')
    os.chmod(filename, 0O666)
    f.write(digestdict_text)
    f.close()


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
    last_entry = datetime.datetime.strptime(last_entry_text, "%Y-%m-%d %H:%M:%S")
    last_email = datetime.datetime.strptime(last_email_text, "%Y-%m-%d %H:%M:%S")
    return digest, last_entry, last_email


def dispose_email(allrecords, last_email, query, force=False):
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
    print('   --- send email to %s' % query['email'])
    topic = query['topic_name']
    sys.stdout.flush()
    query_url = '/query/%d/' % (query['mq_id'])
    message = 'Your active query with Lasair on topic %s\n' % topic
    message_html = 'Your active query with Lasair on <a href=%s>%s</a><br/>' % (query_url, topic)
    for out in allrecords: 
        out_time = datetime.datetime.strptime(out['UTC'], "%Y-%m-%d %H:%M:%S")
        # gather all records that have accumulated since last email
        if force or out_time > last_email:
            if 'diaObjectId' in out:
                diaObjectId = str(out['diaObjectId'])
                message += diaObjectId + '\n'
                message_html += '<a href="%s/objects/%s/">%s</a><br/> \n' % (settings.LASAIR_URL, diaObjectId, diaObjectId)
            else:
                jsonout = json.dumps(out, default=datetime_converter)
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


def dispose_kafka(query_results, topic):
    """ Send out query results by kafka to the given topic.
    """
    conf = {
        'bootstrap.servers': settings.PUBLIC_KAFKA_SERVER,
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': settings.PUBLIC_KAFKA_USERNAME,
        'sasl.password': settings.PUBLIC_KAFKA_PASSWORD
    }

    try:
        p = Producer(conf)
        for out in query_results: 
            jsonout = json.dumps(out, default=datetime_converter)
            p.produce(topic, value=jsonout, callback=kafka_ack)
        p.flush(10.0)   # 10 second timeout
    except Exception as e:
        rtxt = "ERROR in filter/run_active_queries: cannot produce to public kafka"
        rtxt += str(e)
        slack_webhook.send(settings.SLACK_URL, rtxt)
        print(rtxt)
        sys.stdout.flush()


def datetime_converter(o):
    """datetime_converter.

    Args:
        o:
    """
# used by json encoder when it gets a type it doesn't understand
    if isinstance(o, datetime.datetime):
        return o.__str__()


def kafka_ack(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))


def filters(fltr):
    try:
        query_list = fetch_queries()
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.fetch_queries" + str(e))
        return None

    try:
        ntotal = run_queries(fltr, query_list)
        return ntotal
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.run_queries" + str(e))
        return None


def fast_anotation_filters(fltr):
    """run_annotation_queries.
    Pulls the recent content from the kafka topic 'lsst_annotations' 
    Each message has an annotator/topic name, and the diaObjectId that was annotated.
    Queries that have that annotator should run against that object
    """
    try:
        query_list = fetch_queries()
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
    ntotal = run_queries(fltr, query_list, annotation_list)
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
