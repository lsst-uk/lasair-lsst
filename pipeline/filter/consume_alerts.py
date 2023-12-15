"""Consumes stream for ingesting to database
"""
from __future__ import print_function
import os, sys
import insert_query
import argparse, time, json, signal

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

def execute_query(query, msl):
    """ execute_query: run a query and close it, and compalin to slack if failure
    Args:
        query:
        msl:
    """
    try:
        cursor = msl.cursor(buffered=True)
        cursor.execute(query)
        cursor.close()
        msl.commit()
    except Exception as e:
        log = lasairLogging.getLogger("filter")
        log.error('ERROR filter/consume_alerts: object Database insert diaSource failed: %s' % str(e))
        log.info(query)
        raise

def alert_filter(alert, msl):
    """alert_filter: handle a single alert
    Args:
        alert:
        msl:
    """
    # Filter to apply to each alert.
    diaObjectId = alert['diaObject']['diaObjectId']

    # really not interested in alerts that have no detections!
    if len(alert['diaSourcesList']) == 0:
        return 0

    # build the insert query for this object.
    # if not wanted, returns None
    query = insert_query.create_insert_query(alert)
    if not query:
        return 0
    execute_query(query, msl)

    # now ingest the sherlock_classifications
    if 'annotations' in alert:
        annotations = alert['annotations']
        annClass = 'sherlock'
        if annClass in annotations:
            for ann in annotations[annClass]:
                if "transient_object_id" in ann:
                    ann.pop('transient_object_id')
                ann['diaObjectId'] = diaObjectId

                query = insert_query.create_insert_annotation(diaObjectId, annClass, ann, 
                    sherlock_attributes, 'sherlock_classifications', replace=True)
#                f = open('data/%s_sherlock.json'%diaObjectId, 'w')
#                f.write(query)
#                f.close()
                execute_query(query, msl)
    return 1

def kafka_consume(consumer, maxalert):
    """ kafka_consume: consume maxalert alerts from the consumer
        Args:
            consumer: confluent_kafka Consumer
            maxalert: how many to consume
    """
    log = lasairLogging.getLogger("filter")

    # Configure database connection
    try:
        msl = db_connect.local()
    except Exception as e:
        log = lasairLogging.getLogger("filter")
        log.error('ERROR cannot connect to local database', e)
        return -1    # error return

    nalert_in = nalert_out = 0
    startt = time.time()

    while nalert_in < maxalert:
        if sigterm_raised:
            # clean shutdown - stop the consumer and commit offsets
            log.info("Caught SIGTERM, aborting.")
            break

        # Here we get the next alert by kafka
        msg = consumer.poll(timeout=5)
        if msg is None:
            break
        if msg.error():
            continue
        if msg.value() is None:
            continue
        # Apply filter to each alert
        alert = json.loads(msg.value())
        nalert_in += 1
        d = alert_filter(alert, msl)
        nalert_out += d

        if nalert_in%1000 == 0:
            log.info('nalert_in %d nalert_out  %d time %.1f' % \
                (nalert_in, nalert_out, time.time()-startt))
            sys.stdout.flush()
            # refresh the database every 1000 alerts
            # make sure everything is committed
            msl.close()
            msl = db_connect.local()

    log.info('finished %d in, %d out' % (nalert_in, nalert_out))

    ms = manage_status(settings.SYSTEM_STATUS)
    nid  = date_nid.nid_now()
    ms.add({
        'today_filter':nalert_in, 
        'today_filter_out':nalert_out,
        }, nid)

    if nalert_in > 0: return 1   # got some alerts
    else:             return 0   # got no alerts
