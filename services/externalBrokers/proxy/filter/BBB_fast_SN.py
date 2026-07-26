"""
Read Lasair filter and make annotations
"""
import sys
import json
from lasair import lasair_consumer
sys.path.append('../../../../common')
import settings

kafka_server = settings.PUBLIC_KAFKA_READONLY

class Annotator():
    def __init__(self, settings):
        self.settings = settings
        my_topic = settings['TOPIC']
        if 'group_id' in settings:
            group_id = settings['group_id']
        else:
            group_id = 'test123'
        self.consumer = lasair_consumer(kafka_server, group_id, my_topic)

    def next_ann(self):
        try:
            msg = self.consumer.poll()
        except Exception as e:
            return {'error': str(e)}
        if msg is None:
            return {'error': 'msg is None'}
        if msg.error():
            return {'error': msg.error()}
        msg = json.loads(msg.value())

        print(msg)
        diaObjectId = msg['diaObjectId']
        del msg['diaObjectId']
        if msg['BBBFallRate']:
            classification = 'Bazin'
        else:
            classification = 'Exp'
        annotation = {'diaObjectId': diaObjectId,
                      'classification': classification,
                      'classdict': msg
                      }

        return {'annotation': annotation}
