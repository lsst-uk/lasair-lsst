import sys
import os
import logging
import ingest
from fastavro import reader

def read_avro(avroFilePath):
    with open(avroFilePath, 'rb') as fo:
        avro_reader = reader(fo)
#        schema = avro_reader.writer_schema
#        print(schema)

        lsst_alerts = []
        for record in avro_reader:
            lsst_alerts.append(record)
    return lsst_alerts

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        print('Usage: ingest_from_avro file.avro')
        sys.exit()

    lsst_alerts = read_avro(file)
    print('Ingesting %d alerts' % len(lsst_alerts))

    topic_in = ''
    topic_out = 'lsst_ingest'
    group_id = ''
    maxalert = 1000
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("ingest")

    ingester = ingest.Ingester(topic_in, topic_out, group_id, maxalert)

    print('setup')
    ingester.setup_cassandra()
    ingester.setup_producer()

    (nDiaObject, nSSObject, nDiaSource, nDiaSourceDB, nDiaForcedSource, nDiaForcedSourceDB) \
    = ingester._handle_alerts(lsst_alerts)

    print('nDiaObject = %d' % nDiaObject)
    print('nDiaSource = %d' % nDiaSource)
    print('nDiaSourceDB = %d' % nDiaSourceDB)
    print('nDiaForcedSource = %d' % nDiaForcedSource)
    print('nDiaForcedSourceDB = %d' % nDiaForcedSourceDB)

    ingester._end_batch(nDiaObject, nDiaObject, nSSObject, nDiaSource, nDiaSourceDB, nDiaForcedSource, nDiaForcedSourceDB)

