"""
Filter process runner. Sends args to its child and logs the outputs.
It will run continously, running batch after batch. Each batch is a run of the 
child program filtercore.py.

A SIGTERM is handled and passed to the child process, which finishes the batch
and exits cleanly. The SIGTERM also cause this runner process to exit,
which is different from the lockfile check.
Usage:
    ingest.py [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN]

Options:
    --maxalert=MAX     Number of alerts to process per batch, default is defined in settings.KAFKA_MAXALERTS
    --group_id=GID     Group ID for kafka, default is defined in settings.KAFKA_GROUPID
    --topic_in=TIN     Kafka topic to use, default is ztf_sherlock
"""

import os, sys, time, signal
from docopt import docopt
sys.path.append('../../common')
import settings
from datetime import datetime
sys.path.append('../../common/src')
import slack_webhook, lasairLogging
import filtercore

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
topic_in = args.get('--topic_in', 'ztf_sherlock')
group_id = args.get('--group_id', settings.KAFKA_GROUPID)
maxalert = args.get('--maxalert', settings.KAFKA_MAXALERTS)

fltr = filtercore.Filter(topic_in=topic_in, group_id=group_id, maxalert=maxalert)

while not stop:
    log.info('------------- filter_runner running batch at %s' % now())
    nalerts = fltr.run_batch()
    if nalerts == 0:   # process got no alerts, so sleep a few minutes
        log.info('Waiting for more alerts ....')
        time.sleep(settings.WAIT_TIME)

log.info('Exiting filter runner')
