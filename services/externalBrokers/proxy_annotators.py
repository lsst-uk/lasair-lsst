"""Example.

Usage:
    proxy.py [--ann=<item> ...] [--verbose] [--log]

Options:
    --ann=<item>   Annotation (can be specified multiple times).
    --verbose      Enable verbose output.
    --log          Enable logging.
"""

# example: python3 proxy_annotators.py --ann=fink_snn --ann=alerce_stamp --ann=ampel_extragal --verbose
import sys
import importlib
import datetime
from docopt import docopt
sys.path.append('../../common')
import settings
sys.path.append('../../common/src')
import date_nid, annotate_util

args = docopt(__doc__)
ann_names = args["--ann"]      # List[str]
verbose = args["--verbose"]      # bool
log = args["--log"]              # bool
print(f"ann_names = {ann_names}")
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
    ann = settings.proxies[ann_name]
    logf.write(f'Running {ann}\n')
    ann_code = importlib.import_module(ann['CODE'])

    ac = ann_code.Annotator(ann)
    nann = 0
    while 1:
        d = ac.next_ann()
        if not d:
            break
        if verbose:
            logf.write(f'{d}\n')
        annotate_util.insert_annotations_kafka([d])
        nann += 1
        sys.exit()
    logf.write(f'{nann} annotations found\n')
