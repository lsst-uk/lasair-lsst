"""
Read AMPEL classifications from Hopskotch.
"""
import sys
from .hop_reader import hop_reader

class Annotator():
    def __init__(self, settings):
        self.settings = settings
        self.hr = hop_reader(settings)

    def next_ann(self):
        try:
            message = self.hr.poll()
        except TimeoutError:
            return None

        diaObjectId    = message['object']['id']
        classdict = message['features'][0]['features']
        classification = 'infant'

        return {'diaObjectId'   : diaObjectId,
                'topic'         : 'ampel_infant',
                'classification': 'infant',
                'classdict'     : classdict,
                }
