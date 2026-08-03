"""
Annotation/tag test for Lasair using kafka.
Usage:
    ann_test.py <ann_topic>

Arguments:
    <ann_topic>     Annotation topic.

Options:
    -h --help    Show this help message.
"""

import sys
import time
import json
from lasair import lasair_client, lasair_consumer
from docopt import docopt
from util import make_annotator, make_filter_ann, get_diaObjectId
from util import delete_annotator, delete_filter
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import annotate_util

if __name__ == "__main__":
    args = docopt(__doc__)
    username = 'su'
    ann_topic = args['<ann_topic>']
    print(f'Using username {username} and annotator {ann_topic} ')

    if make_annotator(ann_topic, username) == 1:
        print('Cannot run test with existing annotator')
        sys.exit()

    diaObjectId = get_diaObjectId()

    endpoint = "https://lasair-lsst-dev.lsst.ac.uk/api"
    L = lasair_client(settings.API_TOKEN, endpoint=endpoint)

    classdict = {'banana':2, 'mango':None}   # python dict
    ret = L.annotate(
        ann_topic, diaObjectId, 'apple',
        version='0.1', explanation='', classdict=classdict, url='')
    print(ret)

    selected = "objects.diaObjectId"
    tables = f"objects, annotator:{ann_topic}"
    conditions = f"JSON_EXTRACT({ann_topic}.classdict, '$.banana') > 1"
    for niter in range(10):
        c = L.query(selected, tables, conditions, limit=10)
        print(c)
        if len(c) > 0:
            success = True
            break
        print('waiting')
        time.sleep(10)
    else:
        success = False

    # Finally clean up
    print('deleting annotator, annotations')
    delete_annotator(ann_topic)

    if success:
        print('passed test')
        exit(0)
    else:
        print('failed test')
        exit(1)

