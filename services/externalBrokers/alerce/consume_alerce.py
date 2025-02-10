# Pulls from the Alerce Stamp or LC Classifier and pushes into Lasair

import sys
import datetime
import json
import io
import random
import fastavro
import lasair
from urllib.request import urlopen
from confluent_kafka import Consumer, KafkaError
sys.path.append('../../../common')
import settings

def load_json_from_web(url):
  response = urlopen(url)
  data_json = json.loads(response.read())
  return data_json

# light curve classifier is schemaless so need to fetch schema first
schema_url = "https://raw.githubusercontent.com/alercebroker/pipeline/main/schemas/lc_classification_step/output_ztf.avsc"
schema = load_json_from_web(schema_url)

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

def handle_deserealized_record(raw_message, topic):
  bytes_io = io.BytesIO(raw_message.value())

  # Stamp classifier is a normal avro. Read as usual.
  # Reader returns an iterator with one message
  if "stamp_classifier" in topic:
    reader = fastavro.reader(bytes_io)
    record = next(reader)
    r = make_stamp_annotation(record)
    return r

  # LC Classifier is a schemaless abro. Give schema to read.
  # Reader returns a dict.
  elif "lc_classifier_ztf" in topic:
    reader = fastavro.schemaless_reader(bytes_io, schema)
    record = reader
    r = make_lc_annotation(record)
    return r

  else:
    raise Exception(f"No schema loaded for topic {topic}")
    return 0

def connect():
    # create a streamReader
    conf = {
        'bootstrap.servers': settings.ALERCE_KAFKA,
        'group.id'         : settings.ALERCE_GROUP_ID,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism'   : 'SCRAM-SHA-512',
        'sasl.username'    : 'lasair',
        'sasl.password'    : settings.ALERCE_PASSWORD,
        'auto.offset.reset': 'earliest',
    }
    streamReader = Consumer(conf)
    return streamReader

def print_topics(streamReader):
    # print all the topics this streamReader has
    t = list(streamReader.list_topics().topics.keys())
    t = sorted(t)
    print('Topics are ', t)

#############


streamReader = connect()
nalert = 0
nann = 0

if len(sys.argv) < 2:
    print_topics(streamReader)
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

    L = lasair.lasair_client(settings.API_TOKEN, endpoint='https://' + settings.LASAIR_URL + '/api')

    # consume a topic from a streamReader and call handle
    streamReader.subscribe([topic])
    nalert = 0
    while nalert < 5000:  # just do 5000 at a time for now
        msg = streamReader.poll(timeout=20)
        if msg == None:
            break
        r = handle_deserealized_record(msg, topic)
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
    print('\n-- %d annotations from alerce_%s at %s' % (nann, classifier_type, datetime.datetime.now()))
