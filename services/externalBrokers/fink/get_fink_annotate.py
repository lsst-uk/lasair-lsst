import os, sys
import json
from datetime import datetime
import lasair

sys.path.append('../../../common')
import settings
from src import date_nid

sys.path.append('fink-client')
from fink_client.consumer import AlertConsumer

TESTMODE = (len(sys.argv) > 1 and sys.argv[1] == 'TEST')

nid  = date_nid.nid_now()
date = date_nid.nid_to_date(nid)

if TESTMODE:
    logf = sys.stdout
else:
    logfile = settings.SERVICES_LOG +'/'+ date + '.log'
    logf = open(logfile, 'a')

# Lasair client
L = lasair.lasair_client(settings.API_TOKEN, endpoint='https://' + settings.LASAIR_URL + '/api')
topic_out = 'fink'

# Fink configuration
fink_config = {
    'username':          settings.FINK_USERNAME ,
    'bootstrap.servers': settings.FINK_SERVERS,
    'group_id':          settings.FINK_GROUP_ID
}

# Instantiate a consumer
consumer = AlertConsumer(settings.FINK_TOPICS, fink_config)

if TESTMODE:
    d = consumer.available_topics()
    topics = list(d.keys())
    topics.sort()
    for topic in topics: 
        if topic.startswith('fink'):
            print('Found topic:', topic)

nalert = {}
n = 0
maxtimeout = 5
maxalert = 5000
while n < maxalert:
    (topic, alert, version) = consumer.poll(maxtimeout)
    if topic is None:
        break
    if TESTMODE:
        print(alert['objectId'], topic)

    if not topic in settings.FINK_TOPICS:
        continue

    L.annotate(
        topic_out,
        alert['objectId'],
        topic[:16],
        version='0.1',
        explanation='',
        classdict={'classification': topic},
        url='')

    n += 1
    if topic in nalert:
        nalert[topic] += 1
    else:
        nalert[topic] = 1

if n > 0:
    logf.write('\n-- %s from Fink at %s\n' % (nalert, datetime.now()))
