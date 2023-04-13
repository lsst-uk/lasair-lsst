"""
Filter process runner. Sends args to its child and logs the outputs.
It will run continously, running batch after batch. Each batch is a run of the 
child program filter.py.
The runner needs a lockfile -- usually as ~ubuntu/lockfile. If not present
the runner continues, but looking for a lockfile every few minutes.
A SIGTERM is handled and passed to the child process, which finishes the batch
and exits cleanly. The SIGTERM also cause this runner process to exit,
which is different from the lockfile check.
Usage:
    ingest.py [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN]
Options:
    --maxalert=MAX     Number of alerts to process, default is infinite
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, or
"""

import os, sys, time, signal
from docopt import docopt
from filter import run_filter

sys.path.append('../../common')
import settings
from datetime import datetime

from subprocess import Popen, PIPE, STDOUT
sys.path.append('../../common/src')
import slack_webhook, lasairLogging

# if this is True, the runner stops when it can and exits
stop = False

def sigterm_handler(signum, frame):
    global stop
    print('Stopping by SIGTERM')
    stop = True

signal.signal(signal.SIGTERM, sigterm_handler)

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

# Set up the logger
lasairLogging.basicConfig(
    filename='/home/ubuntu/logs/filter.log',
    webhook=slack_webhook.SlackWebhook(url=settings.SLACK_URL),
    merge=True
)
log = lasairLogging.getLogger("filter_runner")

args = docopt(__doc__)

while not stop:
    # check for lockfile
    if not os.path.isfile(settings.LOCKFILE):
        log.info('Lockfile not present, waiting')
        time.sleep(settings.WAIT_TIME)
        continue
    log.info('------------- Filter_runner at %s' % now())
    
    retcode = run_filter(args)

    if retcode == 0:   # process got no alerts, so sleep a few minutes
        log.info('Waiting for more alerts ....')
        time.sleep(settings.WAIT_TIME)

log.info('Exiting')
