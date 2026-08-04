"""
Read AMPEL classifications from Hopskotch.
"""
import sys, json
from .hop_reader import HopReader


class Annotator(HopReader):
    def __init__(self, settings):
        super().__init__(settings)

    def parse(self, message):
        if 'error' in message:
            return message
        diaObjectId    = message['object']['id']
        classdict      = {}
        classification = None
        probs = message['classification'][0]['models'][0]['probabilities']
        probs = {k: v for k, v in sorted(probs.items(), key=lambda item: -item[1])}
        for k,v in probs.items():
            cls = k[2:-1]
            if v > 0.01:
                classdict[cls] = float(v)

        if len(classdict) > 0:
            classification = list(classdict.keys())[0]

        return {'annotation': {
                  'diaObjectId'   : diaObjectId,
                  'topic'         : 'ampel_extragal',
                  'classification': classification,
                  'classdict'     : json.dumps(classdict),
                }
              }
