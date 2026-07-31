"""
Read AMPEL classifications from Hopskotch.
"""
import sys, json
from .hop_reader import hop_reader

class Annotator():
    def __init__(self, settings):
        self.settings = settings
        self.hr = hop_reader(settings)

    def next_ann(self):
        message = self.hr.poll()
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
