"""
Read AMPEL classifications from Hopskotch.
"""
import sys, json
from proxy_annotators import ProxyAnnotator
from .hop_reader import hop_reader

class Annotator(ProxyAnnotator):
    def __init__(self, settings):
        self.hr = hop_reader(settings)

    def next_ann(self):
        message = self.hr.poll()
        if 'error' in message:
            return message

        diaObjectId    = message['object']['id']
        classdict = message['features'][0]['features']
        classification = 'infant'

        return {'annotation': {
                  'diaObjectId'   : diaObjectId,
                  'topic'         : 'ampel_infant',
                  'classification': 'infant',
                  'classdict'     : json.dumps(classdict),
                }
              }
