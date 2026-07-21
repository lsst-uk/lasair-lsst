"""
Annotation/tag test for Lasair using kafka.
Usage:
    ann_test.py <username> <ann_topic> (api | direct_kafka)

Arguments:
    <username>      Username to use.
    <ann_topic>     Announcement topic.
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
from util import delete_annotator, delete_filter
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
    print(f'Using username {username} and annotator {ann_topic} ')

    # make the annotator
    make_annotator(ann_topic, username)

    # make the filter
    filter_name = f'__filt{ann_topic}'
    kafka_topic_name = make_filter_ann(filter_name, username, ann_topic)
    print(f'Filter topic name is {kafka_topic_name}')

    # fins a random object to annotate
    diaObjectId = get_diaObjectId()

    print('making annotations apple and pear')
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

    # check to see what has come through
    # if the annotations went into kafka, we need to wait a while
    print('checking annotations')
    for niter in range(10):
        print(f'sleeping for 10 seconds ...')
        time.sleep(10)

        tags = annotate_util.classifications_for_object(ann_topic, diaObjectId)
        ntags = len(tags)
        print(f'- Found tags for {diaObjectId}/{ann_topic}:', tags)
        if ann_topic.startswith('tags_'):
            right1 = (ntags == 2)   # if tags, apple and pear are there
        else:
            right1 = (ntags == 1)   # if classic, only pear
        if right1: print('success')

        tag = 'apple'
        objs = annotate_util.objects_for_classification(ann_topic, tag)
        print(f'- Found objects for {ann_topic}/{tag}:', objs)
        nobjs1 = len(objs)
        if ann_topic.startswith('tags_'):
            right2 = (nobjs1 == 1)  # if tags, apple is there
        else:
            right2 = (nobjs1 == 0)  # if classic, apple is not there

        tag = 'pear'
        objs = annotate_util.objects_for_classification(ann_topic, tag)
        print(f'- Found objects for {ann_topic}/{tag}:', objs)
        nobjs2 = len(objs)
        right3 = (nobjs2 == 1)  # pear should be there
        if right3: print('success')

        if ntags > 0 or nobjs1 > 0 or nobjs2 > 0:
            break
    else:
        print('Did not see annotations from filter-annotation process')
        right1 = right2 = right3 = False

    # the filter should have produced kafka
    print('Now fetch kafka')
    kafka_server = 'lasair-lsst-dev-kafka_pub.lsst.ac.uk:9092'
    group_id = 'LASAIR1'
    consumer = lasair_consumer(kafka_server, group_id, kafka_topic_name)
    nmessage = 0
    for i in range(5):
        msg = consumer.poll(timeout=10)
        if msg is None:
            if nmessage > 0:
                break
            print('sleeping 5')
            time.sleep(5)
            continue
        if msg.error():
            print(str(msg.error()))
            break
        result = json.loads(msg.value())
        print(result)
        nmessage += 1
    else:
        print('Did not see alerts triggered by annotations')

    print(nmessage, 'Kafka messages')
    right4 = (nmessage >= 1)

    # Don't need these any more
    print('Deleting annotator, annotations, and filter')
    delete_annotator(ann_topic)
    delete_filter(filter_name)

    if right1 and right2 and right3 and right4:
        print('passed test')
        exit(0)
    else:
        print('failed test')
        exit(1)

