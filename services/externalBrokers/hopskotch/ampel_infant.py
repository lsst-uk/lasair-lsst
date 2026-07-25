"""
Read AMPEL classifications from Hopskotch.
"""
import sys
from hop_reader import hop_reader
sys.path.append('../../../common')
import settings

class Annotator()
    def __init__():
        self.hr = hop_reader(topic_in, group_id, is_gcn=False)

    def next_ann():
        try:
            message = hr.poll()
        except TimeoutError:
            return {}

        diaObjectId    = message['object']['id']
        classdict = message['features'][0]['features']
        classification = 'infant'
