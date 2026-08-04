"""
Read AMPEL classifications from Hopskotch.
"""
import sys, json
from proxy_annotators import ProxyAnnotator
from .hop_reader import HopReader


class Annotator(HopReader):
    def __init__(self, settings):
        super().__init__(settings)

    def parse(self, message):
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
