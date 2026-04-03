import sys, os
import datetime
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import lasairLogging
import logging

def fetch_queries(fltr):
    """fetch_queries.
    Get all the stored queries from the main database
    """

    # Fetch all the stored queries from the main database
    cursor = fltr.database_remote.cursor(buffered=True, dictionary=True)
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
        status = fltr.ms.read(fltr.nid)
        if nbytesname in status:
            query_dict['bytes_produced'] = status[nbytesname]

        query_list.append(query_dict)
    return query_list

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

def dispose_query_results(fltr, query, query_results):
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
                if diaObjectId in fltr.message_dict:
                    alert = fltr.message_dict[diaObjectId]
                else:
                    # try to fetch it from cassandra, not yet implemented!
                    fltr.log.info(f'Cannot find lightcurve {diaObjectId} in alert cache')

                if alert:
                    if active == LIGHTCURVE_LITE:
                        q['alert'] = lightcurve_lite(alert)
                    if active == LIGHTCURVE_FULL:
                        q['alert'] = alert

    dispose_kafka(fltr, query_results, query)
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


def dispose_kafka(fltr, query_results, query):
    """ Send out query results by kafka to the given topic.
    """
    producer = fltr.producer
    log = fltr.log
    topic_name = query['topic_name']
    # First decide if this filter has already produced enough
    bp = query.get('bytes_produced', 0)
    bq = query['byte_quota']
    will_produce = (bp < bq) or (bq == -1)

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
                if nalert % 100 == 0:
                    producer.flush()
        producer.flush(10.0)   # 10 second timeout
    except Exception as e:
        rtxt = "ERROR in filter/run_active_queries: cannot produce to public kafka"
        rtxt += str(e)
        log.error(settings.SLACK_URL, rtxt)
        print(rtxt)
        sys.stdout.flush()

    # Record this as produced or rejected
    if will_produce:
        fltr.ms.add({
            topic_name+'_bytes_produced' : nbytes,
            topic_name+'_alerts_produced': nalert,
        }, fltr.nid)
    else:
        fltr.ms.add({
            topic_name+'_bytes_rejected' : nbytes,
            topic_name+'_alerts_rejected': nalert,
        }, fltr.nid)

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
