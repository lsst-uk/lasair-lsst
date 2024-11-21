import os, sys
import json
import datetime
from fink_client.consumer import AlertConsumer
sys.path.append('../../../common')
import settings

not_wanted = ['cutoutDifference',
              'cutoutTemplate',
              'cutoutScience',
              'candidate',
              'prv_candidates']
def fink_content(message):
    """ This function removes the voluminous part of tha alert leaving the Fink added value
    """
    wanted = {k: message[k] for k in message if k not in not_wanted}
    return json.dumps(wanted, indent=2)

# Fink configuration
fink_config = {
    'username':          settings.FINK_USERNAME ,
    'bootstrap.servers': settings.FINK_SERVERS,
    'group_id':          settings.FINK_GROUP_ID
}

# Instantiate a consumer
consumer = AlertConsumer(settings.FINK_TOPICS, fink_config)

nalert = 0
maxtimeout = 5
maxalerts = 5
while nalert < maxalerts:
    (topic, alert, version) = consumer.poll(maxtimeout)
    if topic is None:
        break

    print(topic)
    print(fink_content(alert))
    nalert += 1
if nalert > 0:
    print('\n-- %d from Fink at %s' % (nalert, datetime.datetime.now()))

