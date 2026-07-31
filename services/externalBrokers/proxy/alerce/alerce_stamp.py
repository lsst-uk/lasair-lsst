# Pulls from the Alerce Stamp or LC Classifier and pushes into Lasair
import sys
import json
import io
import fastavro
from confluent_kafka import Consumer, KafkaError
sys.path.append('../../../common/src')
import date_nid

class Annotator():
    def __init__(self, settings):
        self.settings = settings
        if 'group_id' in settings:
            group_id = settings['group_id']
        else:
            group_id = '-001'
        conf = {
            'bootstrap.servers': settings['SERVERS'],
            'group.id'         : settings['ALERCE_NAME'] + group_id,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism'   : 'SCRAM-SHA-512',
            'sasl.username'    : settings['ALERCE_NAME'],
            'sasl.password'    : settings['ALERCE_PASSWORD'],
            'auto.offset.reset': 'earliest',
        }
        self.streamReader = Consumer(conf)

    def next_ann(self):
        if 'DATE' in self.settings:
            date = self.settings['DATE']
        else:
            nid  = date_nid.nid_now()
            date = date_nid.nid_to_date(nid)
        topic = f'stamp_classifier_{date}'
        self.streamReader.subscribe([topic])
        msg = self.streamReader.poll(timeout=20)
        if msg == None:
            return {'error': 'End of stream'}
        bytes_io = io.BytesIO(msg.value())

        # Stamp classifier Rubin is a schemaless abro. Give schema to read.
        # Reader returns a dict.
        try:
            reader = fastavro.reader(bytes_io)
            record = next(reader)
        except:
            return {'error': f'Cannot open {topic}'}

        if self.settings['verbose']:
            result = {'info': f'Got record {str(record)}'}
        else:
            result = {}

        annotation = {}
        classdict = {}
        maxprob = 0
        for k,v in record['probabilities'].items():
            classdict[k] = float('%.3f'%v)
            if v > maxprob:
                annotation['classification'] = k
        maxprob = v
        annotation['diaObjectId'] = record['objectId']
        annotation['classdict']      = classdict
        if annotation['classification'] not in ['VS', 'AGN', 'asteroid', 'bogus']:
            result['annotation'] = annotation
        return result
