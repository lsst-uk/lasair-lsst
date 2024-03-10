""" Transfer local database to main, 
    Write statistics for lasair page and for grafana
"""
import os, sys, datetime, math, time, json, tempfile
import requests, urllib, urllib.parse

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import date_nid, lasairLogging, db_connect, manage_status

def transfer_to_main(batch):
    """ Transfer the local database to the main database
    """
    cmd = 'sudo rm /data/mysql/*.txt'
    os.system(cmd)

    cmd = 'mysql --user=ztf --database=ztf --password=%s < output_csv.sql'
    cmd = cmd % settings.LOCAL_DB_PASS
    if os.system(cmd) != 0:
        log.error('ERROR in filter/filter: cannot build CSV from local database')
        return None

    tablelist = [
        'objects', 
        'sherlock_classifications', 
        'watchlist_hits', 
        'area_hits'
    ]

    commit = True
    for table in tablelist:
        sql  = "LOAD DATA LOCAL INFILE '/data/mysql/%s.txt' " % table
        sql += "REPLACE INTO TABLE %s FIELDS TERMINATED BY ',' " % table
        sql += "ENCLOSED BY '\"' LINES TERMINATED BY '\n'"

        tmpfilename = tempfile.NamedTemporaryFile().name + '.sql'
        f = open(tmpfilename, 'w')
        f.write(sql)
        f.close()

        cmd =  "mysql --user=%s --database=ztf --password=%s --port=%s --host=%s < %s"
        cmd = cmd % (settings.DB_USER_READWRITE, \
                     settings.DB_PASS_READWRITE, \
                     settings.DB_PORT, \
                     settings.DB_HOST, tmpfilename)
        if os.system(cmd) != 0:
            batch.log.error('ERROR in filter/end_batch: cannot push %s local to main database' % table)
            commit = False
        else:
            batch.log.info('%s ingested to main db' % table)

    if commit:
        batch.consumer.commit()
        batch.consumer.close()
        batch.log.info('Kafka committed for this batch')
    else:
        batch.consumer.close()

    return commit

def write_stats(batch, nalerts):
    """ Write the statistics to lasair status and to grafana
    """
    ms = manage_status.manage_status(settings.SYSTEM_STATUS)
    nid = date_nid.nid_now()
    d = batch_statistics()
    ms.set({
        'today_ztf':grafana_today(),
        'today_database':d['count'],
        'total_count': d['total_count'],
        'min_delay': '%.1f' % d['since'],  # hours since most recent alert
        'nid': nid},
        nid)
    for name,td in batch.timers.items():
        td.add2ms(ms, nid)

    if nalerts > 0:
        min_str = "{:d}".format(int(d['min_delay']*60))
        avg_str = "{:d}".format(int(d['avg_delay']*60))
        max_str = "{:d}".format(int(d['max_delay']*60))
    else:
        min_str = "NaN"
        avg_str = "NaN"
        max_str = "NaN"
    #t = int(1000*time.time())
    s  = '#HELP lasair_alert_batch_lag Lasair alert batch lag stats\n'
    s += '#TYPE gauge\n'
    s += 'lasair_alert_batch_lag{type="min"} %s\n' % min_str
    s += 'lasair_alert_batch_lag{type="avg"} %s\n' % avg_str
    s += 'lasair_alert_batch_lag{type="max"} %s\n' % max_str
    try:
        filename = '/var/lib/prometheus/node-exporter/lasair.prom'
        f = open(filename, 'w')
        f.write(s)
        f.close()
    except:
        batch.log.error("ERROR in filter/filter: Cannot open promethus %s" % filename)

def batch_statistics():
    """since_midnight.
    How many objects updated since last midnight
    """
    t = time.time()
    tainow = (time.time() / 86400 + 40587)
    midnight = math.floor(tainow - 0.5) + 0.5

    msl_main = db_connect.readonly()
    cursor = msl_main.cursor(buffered=True, dictionary=True)

    # objects modified since last midnight
    query = 'SELECT count(*) AS count FROM objects WHERE maxTai > %.1f' % midnight
    try:
        cursor.execute(query)
        for row in cursor:
            count = row['count']
            break
    except:
        count = -1

    # total number of objects
    query = 'SELECT count(*) AS total_count, mjdnow()-max(maxTai) AS since FROM objects'

    try:
        cursor.execute(query)
        for row in cursor:
            total_count = row['total_count']
            since = 24 * float(row['since'])
            break
    except:
        total_count = -1
        since = -1

    # statistics for most recent batch
    min_delay = -1
    avg_delay = -1
    max_delay = -1
    msl_local = db_connect.local()
    cursor = msl_local.cursor(buffered=True, dictionary=True)
    query = 'SELECT '
    query += 'tainow()-max(maxTai) AS min_delay, '
    query += 'tainow()-avg(maxTai) AS avg_delay, '
    query += 'tainow()-min(maxTai) AS max_delay '
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
        'total_count': total_count, # number of objects in database
        'count': count,             # number of objects updated since midnight
        'since': since,             # time since last object, hours
        'min_delay': min_delay,     # for grafana min delay in this batch, minutes
        'avg_delay': avg_delay,     # for grafana avg delay in this batch, minutes
        'max_delay': max_delay,     # for grafana max delay in this batch, minutes
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


