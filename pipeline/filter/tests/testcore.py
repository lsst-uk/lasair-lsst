import sys
import datetime
import numbers
import json
import math

from filtercore import Filter

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import date_nid
import db_connect

def now():
    return datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")

class TestFilter(Filter):
    ### TestFilter is subclass of Filter
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    ### set up an AnnotationFilter, after setting up the Filter
    def setup(self):
        # get the Filter object set up 
        super().setup()

    # this method will be called from above when a batch of messages is ready
    def setup_batch(self):
        print('Running setup_batch')

        self.diaObjectIdList = []
        self.h = {
            'alert':{
                'diaObjects':0,
                'diaSources':0,
                'diaForcedSources':0, 
                },
            'annotations':{
                }
            }  # histogram of types
        return

    def post_ingest(self, n_messages):
        print(f'At post_ingest after {n_messages}')
        print(json.dumps(self.h, indent=2))

    def ingest_message_list(self, messageList):
        print('Annotation ingestion starting for ', len(messageList))
        nmessage = 0
        for message in messageList:
            nmessage += self.ingest_message(message)
        return nmessage

    def ingest_message(self, message):
        if 'diaObject' in message:
            self.h['alert']['diaObjects'] += 1
            if 'diaSourcesList' in message:
                self.h['alert']['diaSources'] += len(message['diaSourcesList'])
            if 'diaForcedSourcesList' in message:
                self.h['alert']['diaForcedSources'] += len(message['diaForcedSourcesList'])

        if 'annotations' in message:
            for key,val in message['annotations'].items():
                if key in self.h['annotations']:
                    self.h['annotations'][key] += 1
                else:
                    self.h['annotations'][key] = 1
        return 1
