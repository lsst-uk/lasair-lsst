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

def load_json_from_file(filename):
    data_json = json.loads(open(filename).read())
    return data_json

# need to fetch schema first
#schema_url = "https://raw.githubusercontent.com/alercebroker/pipeline/main/schemas/lc_classification_step/output_ztf.avsc"
#schema = load_json_from_web(schema_url)

schema_filename = 'stamp_classifier_rubin.avsc'
schema = load_json_from_file(schema_filename)

def make_stamp_annotation(record):
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

def handle_deserealized_record(raw_message, topic):
    bytes_io = io.BytesIO(raw_message.value())

    # Stamp classifier Rubin is a schemaless abro. Give schema to read.
    # Reader returns a dict.
    if "stamp_classifier" in topic:
        try:
            reader = fastavro.schemaless_reader(bytes_io, schema)
        except:
            print(f'Cannot open {topic}')
            return 'fail'
        r = make_stamp_annotation(reader)
        return r

    else:
      raise Exception(f"No schema loaded for topic {topic}")
      return None

def connect():
    # create a streamReader
    conf = {
        'bootstrap.servers': settings.ALERCE_KAFKA,
        'group.id'         : settings.ALERCE_NAME + '-001',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism'   : 'SCRAM-SHA-512',
        'sasl.username'    : settings.ALERCE_NAME,
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
    else:
        print('Unknown classifier, quitting')
        sys.exit()

    L = lasair.lasair_client(settings.ALERCE_API_TOKEN, endpoint='https://' + settings.LASAIR_URL + '/api')

    # consume a topic from a streamReader and call handle
    streamReader.subscribe([topic])
    nalert = 0
    while nalert < 50000:
        msg = streamReader.poll(timeout=20)
        if msg == None:
            break
        r = handle_deserealized_record(msg, topic)
        if r == 'fail':
            break
        if r:
            print(r)
            nann += 1
            L.annotate(
                'alerce_' + classifier_type,
                r['diaObjectId'],
                r['classification'],
                version='0.1',
                explanation='',
                classdict=r['classdict'],
                url='')

        nalert += 1
streamReader.close()
print('-- %d of %d from alerce_%s at %s' % (nann, nalert, classifier_type, datetime.datetime.now()))
