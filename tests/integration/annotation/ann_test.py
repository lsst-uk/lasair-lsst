"""
Annotation/tag test for Lasair. 
Usage:
    ann_test.py <username> <ann_topic> (api | direct)

Arguments:
    <username>   Username to use.
    <ann_topic>  Announcement topic.
    api          Use API mode.
    direct       Use direct mode.

Options:
    -h --help    Show this help message.
"""

import sys
import time
import lasair
from docopt import docopt
import api_token
from util import make_annotator, make_filter_ann, get_diaObjectId
from util import delete_annotator, delete_filter, check_annotations
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import annotate

if __name__ == "__main__":
    if settings.WEB_DOMAIN != 'lasair-lsst-dev':
        print('This test can only run on the dev system')
        sys.exit()

    args = docopt(__doc__)
    username = args['<username>']
    ann_topic = args['<ann_topic>']
    print(f'Using username {username} and annotator {ann_topic}')

    make_annotator(ann_topic, username)

    filter_name = f'__filt{ann_topic}'

    make_filter_ann(filter_name, username, ann_topic)
    diaObjectId = get_diaObjectId()

    if args['api']:
        # will use API to annotate
        endpoint = "https://lasair-lsst-dev.lsst.ac.uk/api"
        L = lasair.lasair_client(api_token.API_TOKEN, endpoint=endpoint)
        L.annotate(
            ann_topic, diaObjectId, 'mango',
            version='0.1', explanation='', classdict={}, url='')
        L.annotate(
            ann_topic, diaObjectId, 'papaya',
            version='0.1', explanation='', classdict={}, url='')

    if args['direct']:
        # will annotate directly
        # two annotations "apple" and "pear"
        annotate.insert_annotation_db(diaObjectId, ann_topic, 'apple')
        annotate.insert_annotation_db(diaObjectId, ann_topic, 'pear')
        # two annotations "banana" and "orange"
        annotate.insert_annotation_kafka(diaObjectId, ann_topic, 'banana')
        annotate.insert_annotation_kafka(diaObjectId, ann_topic, 'orange')

    check_annotations(diaObjectId, ann_topic, 'apple')
    check_annotations(diaObjectId, ann_topic, 'pear')
    sleep_time = 10
    print(f'sleeping for {sleep_time} seconds ...')
    time.sleep(sleep_time)

    check_annotations(diaObjectId, ann_topic, 'banana')
    check_annotations(diaObjectId, ann_topic, 'orange')
    check_annotations(diaObjectId, ann_topic, 'mango')

    delete_annotator(ann_topic)
    delete_filter(filter_name)
