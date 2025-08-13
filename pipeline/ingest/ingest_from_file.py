import json
import logging
import ingest

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

filename = '/home/ubuntu/ZTF25aaaachu.lsst'
lsst_alert = json.loads(open(filename).read())

print('handle_alert')
(iDiaObject, iSSObject, iDiaSource, iDiaSourceDB, iDiaForcedSource, iDiaForcedSourceDB) \
    = ingester._handle_alerts([lsst_alert])
