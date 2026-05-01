import sys, os
import datetime
import json
import smtplib

sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import lasairLogging
import logging


def fetch_queries(fltr):
    """fetch_queries.
    Get all the stored queries from the main database
    """

    # Fetch all the stored queries from the main database (that run on alert)
    cursor = fltr.database_remote.cursor(buffered=True, dictionary=True)
    query = 'SELECT mq_id, user, name, email, tables, run, output, byte_quota, real_sql, topic_name '
    query += 'FROM myqueries, auth_user WHERE myqueries.user = auth_user.id AND run > 1'
    cursor.execute(query)

    query_list = []
    for query in cursor:
        query_dict = {
            'mq_id':      query['mq_id'],
            'user':       query['user'],
            'name':       query['name'],
            'run':        query['run'],
            'output':     query['output'],
            'email':      query['email'],
            'tables':     query['tables'],
            'real_sql':   query['real_sql'],
            'topic_name': query['topic_name'],
            'byte_quota': query['byte_quota'],
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
    """ Decide whether to Send out the query results by kafka, add lightcurve if necessary
    """
    if len(query_results) == 0:
        return 0
    output = query['output']

    LIGHTCURVE_LITE = 3
    LIGHTCURVE_FULL = 4

    if not fltr.send_kafka:
        return len(query_results)

    if output == 0:  # muted
        return len(query_results)

    # try to append the lightcurve info
    if output >= LIGHTCURVE_LITE:
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
                    if output == LIGHTCURVE_LITE:
                        q['alert'] = lightcurve_lite(alert)
                    if output == LIGHTCURVE_FULL:
                        q['alert'] = alert

    dispose_kafka(fltr, query_results, query)
    return len(query_results)


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
        rtxt = "ERROR: cannot produce to public kafka"
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
