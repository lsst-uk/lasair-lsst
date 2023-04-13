"""sherlock_batch reads lines containing whitespace separated triplets of objectId, ra, dec and produces
output lines containing the Sherlock Classification, also as ?
(see https://github.com/lsst-uk/lasair4/blob/main/common/schema/sherlock_classifications.sql)

Example: head /mnt/cephfs/missingsherlock/split/xaa | python3 sherlock_batch.py -s /opt/lasair/sherlock_settings.yaml

Output is JSON.
"""

__version__ = "0.1"

#import warnings
import json
import yaml
import argparse
import logging
import sys
from sherlock import transient_classifier
from pkg_resources import get_distribution

sherlock_version = get_distribution("qub-sherlock").version

def classify(conf, log, alerts):
    "send a batch of alerts to sherlock and add the responses to the alerts, return the number of alerts classified"
    
    log.debug('called classify with config: ' + str(conf))
  
    # read Sherlock settings file
    sherlock_settings = {}
    try:
        with open(conf['sherlock_settings'], "r") as f:
            sherlock_settings = yaml.safe_load(f)
    except IOError as e:
        log.error(e)

    annotations = {}

    # make lists of names, ra, dec
    names = []
    ra = []
    dec = []
    for alert in alerts:
        name = alert.get('objectId', alert.get('candid'))
        if not name in annotations:
            if not name in names:
                names.append(name)
                ra.append(alert['ra'])
                dec.append(alert['dec'])

    # set up sherlock
    classifier = transient_classifier(
        log=log,
        settings=sherlock_settings,
        ra=ra,
        dec=dec,
        name=names,
        verbose=0,
        updateNed=False,
        lite=True
    )

    # run sherlock
    cm_by_name = {}
    if len(names) > 0:
        log.log(logging.DEBUG, "running Sherlock classifier on {:d} objects".format(len(names)))
        classifications, crossmatches = classifier.classify()
        log.log(logging.DEBUG, "got {:d} classifications".format(len(classifications)))
        log.log(logging.DEBUG, "got {:d} crossmatches".format(len(crossmatches)))
        # process classfications
        for name in names:
            if name in classifications:
                annotations[name] = { 'classification': classifications[name][0] }
                if len(classifications[name]) > 1:
                    annotations[name]['description'] = classifications[name][1]
        # process crossmatches
        for cm in crossmatches:
            name = cm['transient_object_id']
            if name in cm_by_name:
                cm_by_name[name].append(cm)
            else:
                cm_by_name[name] = [cm]
        for name in names:
            if name in cm_by_name:
                cm = cm_by_name[name]
                if len(cm) > 0:
                    match = cm[0]
                    log.debug("got crossmatch:\n {}".format(json.dumps(match, indent=2)))
                    for key, value in match.items():
                        if key != 'rank':
                            annotations[name][key] = value
    else:
        log.log(logging.INFO, "not running Sherlock as no remaining alerts to process")

    # add the annotations to the alerts
    n = 0
    for alert in alerts:
        name = alert.get('objectId', alert.get('candid'))
        if name in annotations:
            annotations[name]['annotator'] = "https://github.com/thespacedoctor/sherlock/releases/tag/v{}".format(sherlock_version)
            annotations[name]['additional_output'] = "http://lasair-ztf.lsst.ac.uk/api/sherlock/object/" + name
            # placeholders until sherlock returns these
            #annotations[name]['summary']  = 'Placeholder'
            if 'annotations' not in alert:
                alert['annotations'] = {}
            alert['annotations']['sherlock'] = []
            alert['annotations']['sherlock'].append(annotations[name])
            n += 1

    return n


def toCSV(object):
    csv = "{},{},{},".format(object['objectId'], object['ra'], object['dec'])
    sherlock = object['annotations']['sherlock'][0]
    csv += ",".join(map(str,sherlock.values()))
    return csv


def run(conf, log):
    first = True
    print("[")
    batch = 0
    while True:
        if conf['max_batches'] > 0 and batch == conf['max_batches']:
            break
        batch += 1
        objects = []
        n = 0
        for line in sys.stdin:
            try:
                [id, ra, dec] = line.split()
                objects.append( {
                    'objectId': id,
                    'ra':       float(ra),
                    'dec':      float(dec)
                    } )
                n += 1
            except:
                log.info("Failed to parse line, skipping: " + line)
            if n == conf['batch_size']:
                break
        if n == 0: # end of input
            break
        log.info ("batch {}".format(batch))
        classify(conf, log, objects)
        for object in objects:
            if not first:
                print (",")
            else:
                first = False
            print(json.dumps(object, indent=2))
    print("]")


if __name__ == '__main__':
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-n', '--batch_size', type=int, default=1000, help='number of messages to process per batch')
    parser.add_argument('-s', '--sherlock_settings', type=str, default='sherlock.yaml', help='location of Sherlock settings file (default sherlock.yaml)')
    parser.add_argument('-m', '--max_batches', type=int, default=-1, help='max number of batches to process')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    conf = vars(parser.parse_args())

    # set up a logger
    logformat = '%(asctime)s:%(levelname)s:%(filename)s:%(message)s'
    logging.basicConfig(format=logformat, level=logging.WARNING)
    log = logging.getLogger("sherlock_wrapper") 

    run(conf, log)

