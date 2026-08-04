# Pulls from the Alerce LC Classifier and pushes into Lasair

import sys
import json
import io
import fastavro
from confluent_kafka import Consumer, KafkaError
from proxy_annotators import ProxyAnnotator
sys.path.append('../../../common/src')
import date_nid

class Annotator(ProxyAnnotator):
    def __init__(self, settings):
        super().__init__(settings)
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
        schema_filename = 'alerce/stamp_classifier_rubin.avsc'
        self.schema = json.loads(open(schema_filename).read())
        if 'DATE' in self.settings:
            date = self.settings['DATE']
        else:
            nid  = date_nid.nid_now()
            date = date_nid.nid_to_date(nid)
        topic = f'stamp_classifier_{date}'
        self.streamReader.subscribe([topic])

    def next_ann(self):
        msg = self.streamReader.poll(timeout=20)
        if msg == None:
            return {'error': 'End of stream'}
        bytes_io = io.BytesIO(msg.value())

        # Stamp classifier Rubin is a schemaless abro. Give schema to read.
        # Reader returns a dict.
        try:
            reader = fastavro.schemaless_reader(bytes_io, self.schema)
        except:
            return {'error': f'Cannot open alerce_lc'}

        if self.settings['verbose']:
            result = {'info': f'Got record {str(record)}'}
        else:
            result = {}

        annotation = {}
        annotation['diaObjectId'] = record['oid']
        lcc = record['lc_classification']
        annotation['classification'] = lcc['class']
        classdict = {}
        for k,v in lcc['probabilities'].items():
            if v > 0.02:
                classdict[k] = float('%.3f'%v)
        annotation['classdict'] = classdict
        if annotation['classification'] not in ['E', 'Periodic-Other']:
            result['annotation'] = annotation
        return result
