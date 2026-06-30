"""
Read AMPEL classifications from Hopskotch.
"""
import sys
import lasair
from hop_reader import hop_reader
sys.path.append('../../../common')
import settings

def make_classdict(d, topic):
    # convert AMPEL message to objectId and Lasair classdict
    diaObjectId    = d['object']['id']
    classdict      = {}
    classification = None

    if topic == 'ampel.lsst.extragalactic-transients':
        probs = d['classification'][0]['models'][0]['probabilities']
        probs = {k: v for k, v in sorted(probs.items(), key=lambda item: -item[1])}
        for k,v in probs.items():
            cls = k[2:-1]
            if v > 0.01:
                classdict[cls] = float(v)
        if len(classdict) > 0:
            classification = list(classdict.keys())[0]

    elif topic == 'ampel.lsst.extragalactic-infants':
        classdict = d['features'][0]['features']
        classification = 'infant'

    else:
        print(f'Unknown topic {topic}')

    return (diaObjectId, classification, classdict)

def fetch(topic_in, L, topic_out):
    hr = hop_reader(topic_in, group_id, is_gcn=False)
    nalert = 0
    while 1:
        try:
            d = hr.poll()
        except TimeoutError:
            return nalert
        (diaObjectId, classification, classdict) = make_classdict(d, topic_in)
        if classification:
            print(diaObjectId, classdict)
            L.annotate(
                topic_out,
                diaObjectId,
                classification,
                version='0.1',
                explanation='',
                classdict=classdict,
                url='')
        else:
            print('Cannot make classification')
            print(d)
            continue
        nalert += 1

if __name__=="__main__":
    endpoint = "https://lasair-lsst-dev.lsst.ac.uk/api"
    L = lasair.lasair_client(settings.AMPEL_API_TOKEN, endpoint=endpoint)
    if len(sys.argv) > 1:
        group_id = sys.argv[1]
    else:
        group_id = 'test01'

    for i in range(len(settings.HOPSKOTCH_TOPICS_IN)):
        topic_in  = settings.HOPSKOTCH_TOPICS_IN[i]
        topic_out = settings.HOPSKOTCH_TOPICS_OUT[i]
        nalert = fetch(topic_in, L, topic_out)
        print(f'Fetched {nalert} from {topic_in}')
