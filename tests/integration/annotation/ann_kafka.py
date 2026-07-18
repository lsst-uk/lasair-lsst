"""
Annotation/tag test for Lasair using kafka.
Usage:
    ann_test.py <username> <ann_topic> <sleep_time> (api | direct_kafka)

Arguments:
    <username>      Username to use.
    <ann_topic>     Announcement topic.
    <sleep_time>    Seconds to sleep
    api             Use API mode.
    direct_kafka    Use direct kafka mode.

Options:
    -h --help    Show this help message.
"""

import sys
import time
import json
from lasair import lasair_client, lasair_consumer
from docopt import docopt
import api_token
from util import make_annotator, make_filter_ann, get_diaObjectId
from util import delete_annotator, delete_filter, check_annotations
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import annotate_util

if __name__ == "__main__":
    if settings.WEB_DOMAIN != 'lasair-lsst-dev':
        print('This test can only run on the dev system')
        sys.exit()

    args = docopt(__doc__)
    username = args['<username>']
    ann_topic = args['<ann_topic>']
    sleep_time = int(args['<sleep_time>'])
    print(f'Using username {username} and annotator {ann_topic} and sleep time {sleep_time}')

    # make the annotator
    make_annotator(ann_topic, username)

    # make the filter
    filter_name = f'__filt{ann_topic}'
    kafka_topic_name = make_filter_ann(filter_name, username, ann_topic)
    print(f'Filter topic name is {kafka_topic_name}')

    # fins a random object to annotate
    diaObjectId = get_diaObjectId()

    if args['api']:
        # will use API to annotate
        endpoint = "https://lasair-lsst-dev.lsst.ac.uk/api"
        L = lasair_client(api_token.API_TOKEN, endpoint=endpoint)
        L.annotate(
            ann_topic, diaObjectId, 'apple',
            version='0.1', explanation='', classdict={}, url='')
        L.annotate(
            ann_topic, diaObjectId, 'pear',
            version='0.1', explanation='', classdict={}, url='')

    if args['direct_kafka']:
        # two annotations "banana" and "orange"
        annotate_util.insert_annotation_kafka(diaObjectId, ann_topic, 'apple')
        annotate_util.insert_annotation_kafka(diaObjectId, ann_topic, 'pear')

    # if the annotations went into kafka, we need to wait a while
    print(f'sleeping for {sleep_time} seconds ...')
    time.sleep(sleep_time)

    # check to see what has come through
    check_annotations(diaObjectId, ann_topic, 'apple')
    check_annotations(diaObjectId, ann_topic, 'pear')

    # the filter should have produced kafka
    print('Now fetch kafka')
    kafka_server = 'lasair-lsst-dev-kafka_pub.lsst.ac.uk:9092'
    group_id = 'LASAIR1'
    consumer = lasair_consumer(kafka_server, group_id, kafka_topic_name)
    n = 0
    while n < 10:
        msg = consumer.poll(timeout=20)
        if msg is None:
            print('sleeping 5')
            time.sleep(5)
            continue
        if msg.error():
            print(str(msg.error()))
            break
        result = json.loads(msg.value())
        print(result)
        n += 1
    print(n, 'Kafka messages')

    # Finally clean up
    print('deleting annotator, annotations, and filter')
    delete_annotator(ann_topic)
    delete_filter(filter_name)
