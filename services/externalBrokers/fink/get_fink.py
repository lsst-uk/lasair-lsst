import os, sys
sys.path.append('../../common')
from fink_client.consumer import AlertConsumer
import settings

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
while 1:
    (topic, alert, version) = consumer.poll(maxtimeout)
    if topic is None:
        break

    print(topic)
    print(alert)
    nalert += 1
if nalert > 0:
    print('\n-- %d from Fink at %s' % (nalert, datetime.now()))
