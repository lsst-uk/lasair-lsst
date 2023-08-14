"""
This program reads snappy-compressed avro files as published by LSST in
https://github.com/lsst-dm/sample_alert_info

Each alert is then written into a kafka server, without schema.
"""
from confluent_kafka import Producer, KafkaError
import fastavro
import json, sys, os

# where we downloaded the files
dir = '/mnt/cephfs/sample_precursor_alerts'

# the kafka server where the alerts will go
KAFKA = 'lasair-lsst-dev-kafka-0'

# the big files with many alerts each
# the key will be the topic name, the value is the file to read from
filenames = {
'single_ccd_sample3':        # 219 alerts
dir + '/2020-07-06/DECam-HiTS/single_ccd_sample_DECam-HiTS_2020-07-06.avro',
'single_ccd_sample4':       # 217 alerts
dir + '/2020-07-15/DECam-HiTS/single_ccd_sample_DECam-HiTS_2020-07-15.avro',

'single_visit_sample3':      # 6834 alerts
dir + '/2020-07-06/DECam-HiTS/single_visit_sample_DECam-HiTS_2020-07-06.avro',
'single_visit_sample4':     # 6734 alerts
dir + '/2020-07-15/DECam-HiTS/single_visit_sample_DECam-HiTS_2020-07-15.avro',

'all_visits4':               # 678355 alerts
dir + '/2020-07-15/DECam-HiTS/all_visits_DECam-HiTS_2020-07-15.avro',
'all_visits_simulated-sso4': # 500000 alerts
dir + '/2020-11-15/simulated-sso/all_visits_simulated-sso_2020-11-15.avro'
}

conf = {
    'bootstrap.servers': KAFKA,
    'client.id': 'client-1',
}
p = Producer(conf)
tmpfile = 'tmp.avro'

if len(sys.argv) < 2:
    print('Usage: python3 avro_files_to_kafka.py <topic>')
    print('where topic can be')
    for topic in filenames.keys():
        print(topic)
    sys.exit()

topic = sys.argv[1]
filename = filenames[topic]

# topic names derived from file names as above
nalert = 0
with open(filename,'rb') as f:
    freader = fastavro.reader(f)
    schema = freader.writer_schema
#    print(json.dumps(schema, indent=2))
    parsed_schema = fastavro.parse_schema(schema)

    for packet in freader:
        tmp = open(tmpfile, 'wb')
        fastavro.schemaless_writer(tmp, parsed_schema, packet)
        tmp.close()
        tmp = open(tmpfile, 'rb')
        alert = tmp.read()
        tmp.close()
        os.remove(tmpfile)
        if len(alert) > 1000000:  # dump the giant cutouts
            continue
        p.produce(topic, alert)
        p.flush()
        nalert += 1
        if nalert%1000 == 0:
             print('.', end='', flush=True)
print('%d alerts in topic %s' % (nalert,  topic))
