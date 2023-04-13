# Pulls from the Alerce Stamp or LC Classifier and pushes into Lasair

import sys
sys.path.append('../../../common')
from confluent_kafka import Consumer, KafkaError
from fastavro import reader
import lasair
from datetime import datetime
import io
import json
import random
import settings

def make_stamp_annotation(record):
    r = {}
    classdict = {}
    maxprob = 0
    for k,v in record['probabilities'].items():
        classdict[k] = float('%.3f'%v)
        if v > maxprob:
            r['classification'] = k
            maxprob = v
    r['objectId']       = record['objectId']
    r['classdict']      = classdict
    if r['classification'] in ['VS', 'AGN', 'asteroid', 'bogus']:
        return None
    else:
        return r

def make_lc_annotation(record):
    r = {}
    r['objectId'] = record['oid']
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

#############

conf = {
    'bootstrap.servers': settings.ALERCE_KAFKA,
    'group.id'         : settings.ALERCE_GROUP_ID,
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism'   : 'SCRAM-SHA-256',
    'sasl.username'    : 'lasair',
    'sasl.password'    : settings.ALERCE_PASSWORD,
    'auto.offset.reset': 'earliest',
}
streamReader = Consumer(conf)
nalert = 0
nann = 0

if len(sys.argv) < 2:
    # the topics that this server has
    t = list(streamReader.list_topics().topics.keys())
    print('Topics are ', t)
else:
    # content of given topic
    topic = sys.argv[1]
    classifier_type = topic.split('_')[0]
    if classifier_type == 'stamp':
        make_annotation = make_stamp_annotation
    elif classifier_type == 'lc':
        make_annotation = make_lc_annotation
    else:
        print('Unknown classifier, quitting')
        sys.exit()

    L = lasair.lasair_client(settings.API_TOKEN, endpoint='https://lasair-ztf.lsst.ac.uk/api')
#    L = lasair.lasair_client(settings.API_TOKEN)

    streamReader.subscribe([topic])
    while 1:
        msg = streamReader.poll(timeout=5)
        if msg == None: 
            break
        fo = io.BytesIO(msg.value())
        for record in reader(fo):
            r = make_annotation(record)
        if r:
            nann += 1
            L.annotate(
                'alerce_' + classifier_type,
                r['objectId'],
                r['classification'],
                version='0.1',
                explanation='',
                classdict=r['classdict'],
                url='')

        nalert += 1
streamReader.close()
if nann > 0:
    print('\n-- %d annotations from alerce_%s at %s' % (nann, classifier_type, datetime.now()))
