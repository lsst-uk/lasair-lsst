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

    def next_ann(self):
        nid  = date_nid.nid_now()
        date = date_nid.nid_to_date(nid)
        topic = f'stamp_classifier_{date}'
        self.streamReader.subscribe([topic])
        msg = self.streamReader.poll(timeout=20)
        if msg == None:
            return None
        bytes_io = io.BytesIO(msg.value())

        # Stamp classifier Rubin is a schemaless abro. Give schema to read.
        # Reader returns a dict.
        try:
            reader = fastavro.reader(bytes_io)
        except:
            print(f'Cannot open {topic}')
            return None
        r = {}
        classdict = {}
        maxprob = 0
        for k,v in record['probabilities'].items():
            classdict[k] = float('%.3f'%v)
            if v > maxprob:
                r['classification'] = k
        maxprob = v
        r['diaObjectId'] = record['diaObjectId']
        r['classdict']      = classdict
        if r['classification'] in ['VS', 'AGN', 'asteroid', 'bogus']:
            return None
        else:
            return r
