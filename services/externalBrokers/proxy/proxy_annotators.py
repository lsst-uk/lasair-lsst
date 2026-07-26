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
import importlib
import datetime
import signal
from docopt import docopt
sys.path.append('../../../common')
import settings
sys.path.append('../../../common/src')
import date_nid, annotate_util

def handler(signum, frame):
    raise TimeoutError

args = docopt(__doc__)
ann_names = args["--ann"]
maxtry    = int(args["--maxtry"])
group_id  = args["--group_id"]
verbose   = args["--verbose"]
log       = args["--log"]

if verbose:
    print(f"ann_names = {ann_names}")
    print(f'maxtry = {maxtry}')
    print(f'group_id = {group_id}')
    print(f"verbose = {verbose}")
    print(f"log = {log}")

if log:
    # open system services log
    nid  = date_nid.nid_now()
    date = date_nid.nid_to_date(nid)
    logfile = settings.SERVICES_LOG +'/'+ date + '.log'
    logf = open(logfile, 'a')
else:
    logf = sys.stdout
logf.write(f'Annotation proxies at {datetime.datetime.now()}\n')

for ann_name in ann_names:
    if ann_name in settings.proxies:
        ann = settings.proxies[ann_name]
        ann['verbose'] = verbose
        if group_id: 
            ann['group_id'] = group_id
        logf.write(f'Running {ann_name}\n')
    else:
        logf.write(f'Unknown proxy annotator {ann_name}\n')
        continue

    # import the code from the CODE parameter in the settings
    ann_code = importlib.import_module(ann['CODE'])
    ac = ann_code.Annotator(ann)
    nann = 0
    signal.signal(signal.SIGALRM, handler)

    for _try in range(maxtry):
        # expect {'error':'blabla', 'info':'blabla', 'annotation':{'classdict':....}}
        # if error no more in stream
        # if info just report and keep going
        for attempt in range(4):
            signal.alarm(5)
            try:
                result = ac.next_ann()
                signal.alarm(0)
                break  # process the result
            except TimeoutError:
                result = {}
                logf.write('  waiting\n')
        else:
            break  # next proxy annotator

        if 'error' in result:
            logf.write(f'  {result["error"]}\n')
            break
        if 'info' in result:
            logf.write(f'  {result["info"]}\n')
        if 'annotation' in result:
            annotation = result['annotation']
            annotate_util.insert_annotations_kafka([annotation])
            nann += 1
    logf.write(f'  {nann} annotations inserted\n')
