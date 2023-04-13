import datetime
import math
import time
import json
import urllib.parse
import urllib
import requests
import lasairLogging
import db_connect
import settings
import sys
sys.path.append('../../common')
sys.path.append('../../common/src')


def batch_statistics():
    """since_midnight.
    How many objects updated since last midnight
    """
    t = time.time()
    jdnow = (time.time() / 86400 + 2440587.5)
    midnight = math.floor(jdnow - 0.5) + 0.5

    msl_main = db_connect.readonly()
    cursor = msl_main.cursor(buffered=True, dictionary=True)

    # objects modified since last midnight
    query = 'SELECT count(*) AS count FROM objects WHERE jdmax > %.1f' % midnight
    try:
        cursor.execute(query)
        for row in cursor:
            count = row['count']
            break
    except:
        count = -1

    # total number of objects
    query = 'SELECT count(*) AS total_count, jdnow()-max(jdmax) AS since FROM objects'

    try:
        cursor.execute(query)
        for row in cursor:
            total_count = row['total_count']
            since = 24 * float(row['since'])
            break
    except:
        total_count = -1

    # statistics for most recent batch
    min_delay = -1
    avg_delay = -1
    max_delay = -1
    msl_local = db_connect.local()
    cursor = msl_local.cursor(buffered=True, dictionary=True)
    query = 'SELECT '
    query += 'jdnow()-max(jdmax) AS min_delay, '
    query += 'jdnow()-avg(jdmax) AS avg_delay, '
    query += 'jdnow()-min(jdmax) AS max_delay '
    query += 'FROM objects'
    try:
        cursor.execute(query)
        for row in cursor:
            min_delay = 24 * 60 * float(row['min_delay'])  # minutes
            avg_delay = 24 * 60 * float(row['avg_delay'])  # minutes
            max_delay = 24 * 60 * float(row['max_delay'])  # minutes
            break
    except:
        pass

    return {
        'total_count': total_count,  # number of objects in database
        'count': count,             # number of objects updated since midnight
        'since': since,             # time since last object, hours
        'min_delay': min_delay,     # min delay in this batch, minutes
        'avg_delay': avg_delay,     # avg delay in this batch, minutes
        'max_delay': max_delay,     # max delay in this batch, minutes
    }


def grafana_today():
    """since_midnight.
    How many objects reported today from ZTF
    """
    g = datetime.datetime.utcnow()
    date = '%4d%02d%02d' % (g.year, g.month, g.day)
    url = 'https://monitor.alerts.ztf.uw.edu/api/datasources/proxy/7/api/v1/query?query='
    urltail = 'sum(kafka_log_log_value{ name="LogEndOffset" , night = "%s", program = "MSIP" }) - sum(kafka_log_log_value{ name="LogStartOffset", night = "%s", program="MSIP" })' % (date, date)

    try:
        urlquote = url + urllib.parse.quote(urltail)
        resultjson = requests.get(urlquote,
                                  auth=(settings.GRAFANA_USERNAME, settings.GRAFANA_PASSWORD))
        result = json.loads(resultjson.text)
        alertsstr = result['data']['result'][0]['value'][1]
        today_candidates_ztf = int(alertsstr) // 4
    except Exception as e:
        log = lasairLogging.getLogger("filter")
        log.info('Cannot parse grafana: %s' % str(e))
        today_candidates_ztf = -1

    return today_candidates_ztf


if __name__ == "__main__":
    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("ingest_runner")

    print('Grafana today:', grafana_today())
    print('Batch statistics:', batch_statistics())
