import os, sys
import json
import datetime
from fink_client.consumer import AlertConsumer
sys.path.append('../../../common')
import settings

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

# Fink configuration
fink_config = {
    'username':          settings.FINK_USERNAME ,
    'bootstrap.servers': settings.FINK_SERVERS,
#    'group.id':          settings.FINK_GROUP_ID
    'group.id':          'bla15'
}

print(fink_config)

# Instantiate a consumer
consumer = AlertConsumer(settings.FINK_TOPICS, fink_config)

nalert = 0
maxtimeout = 5
maxalerts = 5
while nalert < maxalerts:
    (topic, alert, version) = consumer.poll(maxtimeout)
    if topic is None:
        break

    diaObjectId = alert['diaSource']['diaObjectId']
    classdict = alert['clf']
    try:
        classification = classes[classdict['cats_class']]
    except:
        classification = 'Unknown'
    print(diaObjectId, classification, classdict)
    nalert += 1
if nalert > 0:
    print('\n-- %d from Fink at %s' % (nalert, datetime.datetime.now()))

