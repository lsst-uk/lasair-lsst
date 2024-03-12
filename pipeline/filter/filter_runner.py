"""
Filter process runner. Sends args to its child and logs the outputs.
It will run continously, running batch after batch. Each batch is a run of the 
child program filter.py.

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
    --topic_in=TIN     Kafka topic to use
"""

import os, sys, time, signal
from docopt import docopt
sys.path.append('../../common')
import settings
from datetime import datetime
sys.path.append('../../common/src')
import slack_webhook, lasairLogging
import filter

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

# Deal with arguments
# It's fine to use None as a default here as Filter will use sensible defaults if necessary
args = docopt(__doc__)
topic_in = args.get('--topic_in')
group_id = args.get('--group_id')
maxalert = args.get('--maxalert')

while not stop:
    log.info('------------- filter_runner running batch at %s' % now())

    fltr = filter.Filter(topic_in=topic_in, group_id=group_id, maxalert=maxalert)
    nalerts = fltr.run_batch()
    if nalerts == 0:   # process got no alerts, so sleep a few minutes
        log.info('Waiting for more alerts ....')
        time.sleep(settings.WAIT_TIME)

log.info('Exiting filter runner')
