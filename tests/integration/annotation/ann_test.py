import sys
import time
import lasair
import api_token
from util import make_annotator, make_filter_ann, get_diaObjectId
from util import delete_annotator, delete_filter, check_annotations
sys.path.append('../../../common')
import settings

if __name__ == "__main__":
    if settings.WEB_DOMAIN != 'lasair-lsst-dev':
        print('This test can only run on the dev system')
        sys.exit()

    username = 'royg'

#    ann_topic = f'tags_{username}'    # testing tags
    ann_topic = '__annot'            # testing classic annotations

    method = 'direct'
    method = 'api'

    make_annotator(ann_topic, username)

    filter_name = f'__filt{ann_topic}'

    make_filter_ann(filter_name, username, ann_topic)
    diaObjectId = get_diaObjectId()

    if method == 'api':
        endpoint = "https://lasair-lsst-dev.lsst.ac.uk/api"
        L = lasair.lasair_client(api_token.API_TOKEN, endpoint=endpoint)
        classification = 'mango'
        # one annotation "apple"
        L.annotate(
            ann_topic, diaObjectId, classification,
            version='0.1', explanation='', classdict={}, url='')

    elif method == 'direct':
        # two annotations "apple" and "pear"
        make_annotations_db(diaObjectId, ann_topic)
        # two annotations "banana" and "orange"
        make_annotations_kafka(diaObjectId, ann_topic)
    else:
        print(f'unknown method {method}')
        sys.exit()

    check_annotations(diaObjectId, ann_topic, 'apple')
    check_annotations(diaObjectId, ann_topic, 'pear')
    sleep_time = 10
    print(f'sleeping for {sleep_time} seconds ...')
    time.sleep(sleep_time)

    check_annotations(diaObjectId, ann_topic, 'banana')
    check_annotations(diaObjectId, ann_topic, 'orange')
    check_annotations(diaObjectId, ann_topic, 'mango')

    delete_annotator(ann_topic, True)
    delete_filter(filter_name)
