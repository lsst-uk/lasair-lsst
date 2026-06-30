import os, sys
import json
from datetime import datetime
import lasair

sys.path.append('../../../common')
import settings
from src import date_nid

sys.path.append('fink-client')
from fink_client.consumer import AlertConsumer

""" classifications, see https://lsst.fink-portal.org/schemas
CATS classifier broad class prediction with the highest probability. -1= not processed,
11=SN-like,
12=Fast (e.g. KN, ulens, Novae, ...),
13=Long (e.g. SLSN, TDE, ...),
21=Periodic (e.g. RRLyrae, EB, ...),
22=Non-periodic (e.g. AGN).
See https://arxiv.org/abs/2404.08798 Available from fink_broker_version 4.0 and fink_science_version 8.26.0.
"""
classes = {11: 'SN-like', 12: 'Fast', 13: 'Long', 21:'Periodic', 22:'NonPeriodic'}

nid  = date_nid.nid_now()
date = date_nid.nid_to_date(nid)

TESTMODE = (len(sys.argv) > 1 and sys.argv[1] == 'TEST')

if TESTMODE:
    logf = sys.stdout
else:
    logfile = settings.SERVICES_LOG +'/'+ date + '.log'
    logf = open(logfile, 'a')

# Lasair client
L = lasair.lasair_client(settings.FINK_API_TOKEN, endpoint='https://' + settings.LASAIR_URL + '/api')

# Fink configuration
fink_config = {
    'username':          settings.FINK_USERNAME ,
    'bootstrap.servers': settings.FINK_SERVERS,
    'group.id':          settings.FINK_GROUP_ID
}

# Instantiate a consumer
consumer = AlertConsumer(settings.FINK_TOPICS, fink_config)

nalert = 0
maxtimeout = 5
maxalert = 5000
topic_out = 'Extragalactic_bright'
while nalert < maxalert:
    (topic, alert, version) = consumer.poll(maxtimeout)
    if topic is None:
        break
    diaObjectId = alert['diaSource']['diaObjectId']
    classdict = alert['clf']
    try:
        classification = classes[classdict['cats_class']]
    except:
        classification = 'Unknown'
    if TESTMODE:
        print(diaObjectId, classification, classdict)

    L.annotate(
        topic_out,
        diaObjectId,
        classification,
        version='0.1',
        explanation='',
        classdict=classdict,
        url='')

    nalert += 1

if nalert > 0:
    logf.write('\n-- %s from Fink at %s\n' % (nalert, datetime.now()))
