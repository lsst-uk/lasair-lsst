import os, sys
from datetime import datetime
import lasair

sys.path.append('../../../common')
import settings
from src import date_nid

sys.path.append('fink-client')
from fink_client.consumer import AlertConsumer

nid  = date_nid.nid_now()
date = date_nid.nid_to_date(nid)
logfile = settings.SERVICES_LOG +'/'+ date + '.log'
logf = open(logfile, 'a')

# Lasair client
L = lasair.lasair_client(settings.API_TOKEN, endpoint='https://lasair-ztf.lsst.ac.uk/api')
#L = lasair.lasair_client(settings.API_TOKEN')
topic_out = 'fink'

# Fink configuration
fink_config = {
    'username':          settings.FINK_USERNAME ,
    'bootstrap.servers': settings.FINK_SERVERS,
    'group_id':          settings.FINK_GROUP_ID
}

# Instantiate a consumer
consumer = AlertConsumer(settings.FINK_TOPICS, fink_config)

#d = consumer.available_topics()
#topics = list(d.keys())
#topics.sort()
#for topic in topics: 
#    print(topic)

nalert = {}
n = 0
maxtimeout = 5
while 1:
    (topic, alert, version) = consumer.poll(maxtimeout)
    if topic is None:
        break
    print(topic)

    objectId = alert['objectId']
    classification = topic[:16]
    classdict = {}

    try: classdict['rf_snia_vs_nonia']:   float(alert['rf_snia_vs_nonia']) 
    except: pass

    try: classdict['snn_snia_vs_nonia']:  float(alert['snn_snia_vs_nonia']) 
    except: pass

    try: classdict['snn_sn_vs_all']:      float(alert['snn_sn_vs_all']) 
    except: pass

    try: classdict['rf_kn_vs_nonkn']:     float(alert['rf_kn_vs_nonkn']) 
    except: pass

    try: classdict['anomaly_score']:      float(alert['anomaly_score']) 
    except: pass

    L.annotate(
        topic_out,
        objectId,
        classification,
        version='0.1',
        explanation='',
        classdict=classdict,
        url='')

    n += 1
    if topic in nalert:
        nalert[topic] += 1
    else:
        nalert[topic] = 1

if n > 0:
    logf.write('\n-- %s from Fink at %s\n' % (nalert, datetime.now()))
