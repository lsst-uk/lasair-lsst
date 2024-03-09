"""Consumes stream for ingesting to database
"""
from __future__ import print_function
import os, sys, argparse, time, json, signal
import make_features

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import lasairLogging, db_connect, date_nid
from manage_status import manage_status

# If we catch a SIGTERM, set a flag
sigterm_raised = False

def sigterm_handler(signum, frame):
    global sigterm_raised
    sigterm_raised = True

signal.signal(signal.SIGTERM, sigterm_handler)

sherlock_attributes = [
    "classification",
    "diaObjectId",
    "association_type",
    "catalogue_table_name",
    "catalogue_object_id",
    "catalogue_object_type",
    "raDeg",
    "decDeg",
    "separationArcsec",
    "northSeparationArcsec",
    "eastSeparationArcsec",
    "physical_separation_kpc",
    "direct_distance",
    "distance",
    "z",
    "photoZ",
    "photoZErr",
    "Mag",
    "MagFilter",
    "MagErr",
    "classificationReliability",
    "major_axis_arcsec",
    "annotator",
    "additional_output",
    "description",
    "summary",
]

def execute_query(batch, query):
    """ execute_query: run a query and close it, and compalin to slack if failure
    Args:
        batch:
        query:
    """
    try:
        cursor = batch.local_database.cursor(buffered=True)
        cursor.execute(query)
        cursor.close()
        batch.local_database.commit()
    except Exception as e:
        batch.log.error('ERROR filter/consume_alerts: object Database insert diaSource failed: %s' % str(e))
        batch.log.info(query)
        raise

def handle_alert(batch, alert):
    """alert_filter: handle a single alert
    Args:
        batch:
        alert:
    """
    # Filter to apply to each alert.
    diaObjectId = alert['diaObject']['diaObjectId']

    # really not interested in alerts that have no detections!
    if len(alert['diaSourcesList']) == 0:
        return 0

    # build the insert query for this object.
    # if not wanted, returns None
    query = make_features.create_insert_query(alert)
    if not query:
        return 0
    execute_query(batch, query)

    # now ingest the sherlock_classifications
    if 'annotations' in alert:
        annotations = alert['annotations']
        annClass = 'sherlock'
        if annClass in annotations:
            for ann in annotations[annClass]:
                if "transient_object_id" in ann:
                    ann.pop('transient_object_id')
                ann['diaObjectId'] = diaObjectId

                query = make_features.create_insert_annotation(diaObjectId, annClass, ann, 
                    sherlock_attributes, 'sherlock_classifications', replace=True)
#                f = open('data/%s_sherlock.json'%diaObjectId, 'w')
#                f.write(query)
#                f.close()
                execute_query(batch, query)
    return 1

def consume_alerts(batch):
    """ kafka_consume: consume maxalert alerts from the consumer
        Args:
            consumer: confluent_kafka Consumer
            maxalert: how many to consume
    """
    nalert_in = nalert_out = 0
    startt = time.time()

    while nalert_in < batch.maxalert:
        if sigterm_raised:
            # clean shutdown - stop the consumer and commit offsets
            batch.log.info("Caught SIGTERM, aborting.")
            break

        # Here we get the next alert by kafka
        msg = batch.consumer.poll(timeout=5)
        if msg is None:
            break
        if msg.error():
            continue
        if msg.value() is None:
            continue
        # Apply filter to each alert
        alert = json.loads(msg.value())
        nalert_in += 1
        d = handle_alert(batch, alert)
        nalert_out += d

        if nalert_in%1000 == 0:
            batch.log.info('nalert_in %d nalert_out  %d time %.1f' % \
                (nalert_in, nalert_out, time.time()-startt))
            sys.stdout.flush()
            # refresh the database every 1000 alerts
            # make sure everything is committed
            batch.local_database.close()
            batch.local_database = db_connect.local()

    batch.log.info('finished %d in, %d out' % (nalert_in, nalert_out))

    ms = manage_status(settings.SYSTEM_STATUS)
    nid  = date_nid.nid_now()
    ms.add({
        'today_filter':nalert_in, 
        'today_filter_out':nalert_out,
        }, nid)

    return nalert_out
