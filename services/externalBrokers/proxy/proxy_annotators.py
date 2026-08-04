"""Example.

Usage:
    proxy_annotators.py [--ann=<item> ...] 
                        [--maxtry=<maxtry>] 
                        [--group_id=<group_id] 
                        [--verbose] 
                        [--log]

Options:
    --ann=<item>           Annotation (can be specified multiple times).
    --maxtry=<maxtry>      Maximum annotations per annotator [default: 1000000]
    --group_id=<group_id>  Group_id to be used for Kafka consumer
    --verbose              Enable verbose output.
    --log                  Enable logging.
"""

# example: python3 proxy_annotators.py --ann=fink_snn --ann=alerce_stamp --ann=ampel_extragal --verbose
import sys
import io
import importlib
import datetime
import signal
from docopt import docopt
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import date_nid, annotation_util


class ProxyAnnotator():

    def __init__(self, settings):
        self.settings = settings

    def next_ann(self) -> dict:
        """Get the next available annotation."""
        raise NotImplementedError("Method must be implemented in subclass")


def handler(signum, frame):
    raise TimeoutError


signal.signal(signal.SIGALRM, handler)


def parse_args():
    args = docopt(__doc__)
    argdict =  {
        "ann_names": args["--ann"],
        "maxtry"   : int(args["--maxtry"]),
        "group_id" : args["--group_id"],
        "verbose"  : args["--verbose"],
        "log"      : args["--log"],
    }
    if argdict['verbose']:
        print(f"ann_names = {argdict['ann_names']}")
        print(f"maxtry =    {argdict['maxtry']}")
        print(f"group_id =  {argdict['group_id']}")
        print(f"verbose =   {argdict['verbose']}")
        print(f"log =       {argdict['log']}")

    # with no list of annotators, print the possible names
    if len(argdict['ann_names']) == 0:
        print('List of proxy annotators: ')
        for ann in settings.proxies.keys():
            print(f'--ann={ann} ', end='')
        print()

    return argdict


def get_log_stream(log: str):
    if not log:
        return sys.stdout
    nid = date_nid.nid_now()
    date = date_nid.nid_to_date(nid)
    logfile = f"{settings.SERVICES_LOG}/{date}.log"
    return open(logfile, "a")


def load_annotator(ann: dict) -> ProxyAnnotator:
    module = importlib.import_module(ann["CODE"])
    return module.Annotator(ann)


def get_next_annotation(ac, retries=4, timeout=5, logger=sys.stdout):
    for _ in range(retries):
        signal.alarm(timeout)
        try:
            result = ac.next_ann()
            signal.alarm(0)
            return result
        except TimeoutError:
            logger.write("  waiting\n")
    return None


def process_annotator(ac, maxtry, logger):
    inserted = 0
    for _ in range(maxtry):
        result = get_next_annotation(ac, logger=logger)
        if result is None:
            break
# expect {'error':'blabla', 'info':'blabla', 'annotation':{'classdict':....}}
        if "error" in result:
            logger.write(f'  {result["error"]}\n')
            break
        if "info" in result:
            logger.write(f'  {result["info"]}\n')
        if "annotation" in result:
            annotation_util.insert_annotations_kafka( [result["annotation"]])
            inserted += 1
    return inserted


def main():
    argdict = parse_args()
    logf = get_log_stream(argdict['log'])
    logf.write(f'Annotation proxies at {datetime.datetime.now()}\n')

    for ann_name in argdict['ann_names']:
        if ann_name in settings.proxies:
            ann = settings.proxies[ann_name]
            ann['verbose'] = argdict['verbose']
            if argdict['group_id']:
                ann['group_id'] = argdict['group_id']
            logf.write(f'Running {ann_name}\n')
        else:
            logf.write(f'Unknown proxy annotator {ann_name}\n')
            continue

        ac = load_annotator(ann)
        inserted = process_annotator(ac, argdict["maxtry"], logf)
        logf.write(f"  {inserted} annotations inserted\n")


if __name__ == "__main__":
    main()
