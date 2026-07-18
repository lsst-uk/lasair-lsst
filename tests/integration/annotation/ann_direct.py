"""
Annotation/tag test for Lasair with direct database calls.
Usage:
    ann_direct.py <username> <ann_topic>

Arguments:
    <username>      Username to use.
    <ann_topic>     Announcement topic.

Options:
    -h --help    Show this help message.
"""

import sys
import time
import json
import lasair
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
    print(f'Using username {username} and annotator {ann_topic}')

    # make the annotator
    make_annotator(ann_topic, username)

    # fins a random object to annotate
    diaObjectId = get_diaObjectId()

    # two annotations
    print('inserting annotations')
    annotate_util.insert_annotation_db(diaObjectId, ann_topic, 'apple')
    annotate_util.insert_annotation_db(diaObjectId, ann_topic, 'pear')

    # check to see what has come through
    check_annotations(diaObjectId, ann_topic, 'apple')
    check_annotations(diaObjectId, ann_topic, 'pear')

    # Finally clean up
    print('deleting annotator, annotations')
    delete_annotator(ann_topic)
