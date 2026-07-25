# Pulls from the Alerce LC Classifier and pushes into Lasair

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
        conf = {
            'bootstrap.servers': settings['SERVERS'],
            'group.id'         : settings['ALERCE_NAME'] + '-001',
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism'   : 'SCRAM-SHA-512',
            'sasl.username'    : settings['ALERCE_NAME'],
            'sasl.password'    : settings['ALERCE_PASSWORD'],
            'auto.offset.reset': 'earliest',
        }
        self.streamReader = Consumer(conf)
        schema_filename = 'alerce/stamp_classifier_rubin.avsc'
        self.schema = json.loads(open(schema_filename).read())

    def next_ann(self):
        nid  = date_nid.nid_now()
        date = date_nid.nid_to_date(nid)
        topic = f'stamp_classifier_{date}'
        topic = 'stamp_classifier_20260717'   # HACK
        self.streamReader.subscribe([topic])
        msg = self.streamReader.poll(timeout=20)
        if msg == None:
            return None
        bytes_io = io.BytesIO(msg.value())

        # Stamp classifier Rubin is a schemaless abro. Give schema to read.
        # Reader returns a dict.
        try:
            reader = fastavro.schemaless_reader(bytes_io, self.schema)
        except:
            print(f'Cannot open {topic}')
            return None

        r['diaObjectId'] = record['oid']
        lcc = record['lc_classification']
        r['classification'] = lcc['class']
        classdict = {}
        for k,v in lcc['probabilities'].items():
            if v > 0.02:
                classdict[k] = float('%.3f'%v)
        r['classdict'] = classdict
        if r['classification'] in ['E', 'Periodic-Other']:
            return None
        else:
            return r

