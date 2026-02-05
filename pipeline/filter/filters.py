""" Runs the user's queries. 
Fetch them from database, construct SQL, execute, produce kafka

(1) fetch_queries(msl_remote, ms, nid) 
gets all the queries from the remote database. ms is manage_status and nid is today.

(2) run_queries(batch, query_list, ms, nid):
Uses query_list runs all the queries against local database

(3) run_query(query, msl)
Run a specific query and return query_results

(4) dispose_query_results(query, query_results, fltr, ms, nid)
Deal with the query results

(4a) fetch_digest(topic_name):
    Get the digest file from shared storage

(4b) dispose_email(allrecords, last_email, query):
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

def run_queries(fltr, query_list, ms, nid):
    """
    When annotation_list is None, it runs all the queries against the local database
    When not None, runs some queires agains a specific object, using the main database
    """

    ntotal = 0
    for query in query_list:
        n = 0
        t = time.time()
        query_results = run_query(query, fltr.database)
        n += dispose_query_results(query, query_results, fltr, ms, nid)
        t = time.time() - t
        if n > 0:
            print('   %s(%d) got %d in %.1f seconds' % (query['topic_name'], query['active'], n, t))
            sys.stdout.flush()
        ntotal += n
    return ntotal

def run_query(query, msl):
    """run_query.
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
            last_email = dispose_email(allrecords, last_email, query)
        utcnow = datetime.datetime.now(datetime.UTC)
        write_digest(allrecords, query['topic_name'], utcnow, last_email)

    if active >= 2:
        # send results by kafka on given topic
        if fltr.send_kafka:
            if active == 3:   # append lightcurve lite
                for q in query_results:
                    try:
                        diaObjectId = q['diaObjectId']
                        q['alert'] = lightcurve_lite(fltr.alert_dict[diaObjectId])
                    except:
                        pass
            if active == 4:   # append full alert
                for q in query_results:
                    try:
                        diaObjectId = q['diaObjectId']
                        q['alert'] = fltr.alert_dict[diaObjectId]
                    except:
                        pass
        dispose_kafka(query_results, query, ms, nid)

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
        out_time = tutc(out['UTC'])
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


def dispose_kafka(query_results, query, ms, nid):
    """ Send out query results by kafka to the given topic.
    """
    topic_name = query['topic_name']
    # First decide if this filter has already produced enough
    bp = query.get('bytes_produced', 0)
    bq = query.get('byte_quota', settings.MAX_KAFKA_BYTES_PER_FILTER)
    will_produce = (bp < bq)

    # Kafka produce config
    conf = {
        'bootstrap.servers': settings.PUBLIC_KAFKA_SERVER,
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': settings.PUBLIC_KAFKA_USERNAME,
        'sasl.password': settings.PUBLIC_KAFKA_PASSWORD
    }

    nbytes = 0
    nalert = 0
    try:
        p = Producer(conf)
        for out in query_results: 
            jsonout = json.dumps(out, default=datetime_converter)
            nbytes += len(jsonout)
            nalert += 1
            if will_produce:
                p.produce(topic_name, value=jsonout, callback=kafka_ack)
        p.flush(10.0)   # 10 second timeout
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
    # first get the user queries from the database that the webserver uses
    msl_remote = db_connect.remote()

    # how many bytes has each filter already produced
    ms = manage_status.manage_status(msl=msl_remote)
    nid = date_nid.nid_now()

    try:
        query_list = fetch_queries(msl_remote, ms, nid)
    except Exception as e:
        fltr.log.error("ERROR in filter/run_active_queries.fetch_queries" + str(e))
        return None

    ntotal = run_queries(fltr, query_list, ms=ms, nid=nid)
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
