import os, sys
import json
import logging
import ingest

if len(sys.argv) > 1:
    dir          = sys.argv[1]
else:
    print("Usage: make_sample_alert.py <directory>")
    sys.exit()

topic_in = ''
topic_out = 'ztf_ingest'
group_id = ''
maxalert = 1000
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ingest")

ingester = ingest.Ingester(
    topic_in, topic_out, group_id, maxalert, nocutouts=True)

print('setup')
ingester.setup_cassandra()
ingester.setup_producer()

alerts = []
for file in os.listdir(dir):
    alerts.append(json.loads(open(dir +'/'+ file).read()))

print('ingesting %s files' % len(alerts))

(iDiaObject, iSSObject, iDiaSource, iDiaSourceDB, iDiaForcedSource, iDiaForcedSourceDB) \
    = ingester._handle_alerts(alerts)

print('iDiaObject = %d' % iDiaObject)
print('iDiaSource = %d' % iDiaSource)
print('iDiaSourceDB = %d' % iDiaSourceDB)
print('iDiaForcedSource = %d' % iDiaForcedSource)
print('iDiaForcedSourceDB = %d' % iDiaForcedSourceDB)
