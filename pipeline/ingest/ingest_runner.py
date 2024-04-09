"""
Ingest proess runner. Takes the --nprocess arg and starts that many versions of ingest.py, 
with other arguments sent there, also logs the outputs. 
If maxalert is specified, it does that many for each process then exits,
otherwise maxalert is the largest possible. 
SIGTERM is passed to those children and dealt with properly.
Usage:
    ingest.py [--maxalert=MAX]
              [--nprocess=nprocess]
              [--group_id=GID]
              [--topic_in=TIN | --nid=NID]
              [--topic_out=TOUT]

Options:
    --maxalert=MAX       Number of alerts to process, default is infinite
    --nprocess=nprocess  Number of processes [default: 1]
    --group_id=GID       Group ID for kafka, default is from settings
    --topic_in=TIN       Kafka topic to use, or
    --nid=NID            ZTF night number to use (default today)
    --topic_out=TOUT     Kafka topic for output [default:ztf_sherlock]
"""
import sys
from docopt import docopt
from multiprocessing import Process

from ingest import run_ingest

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import slack_webhook, lasairLogging


def setup_proc(n, nprocess, args):
    # Set up the logger
    lasairLogging.basicConfig(
        filename=f"/home/ubuntu/logs/ingest-{n}.log",
        webhook=slack_webhook.SlackWebhook(url=settings.SLACK_URL),
        merge=True
    )
    log = lasairLogging.getLogger("ingest_runner")
    log.info(f"Starting ingest runner process {n} of {nprocess}")
    try:
        nalerts = run_ingest(args, log=log)
        log.debug(f'Ingested {nalerts} alerts')
    except Exception as e:
        log.exception('Exception')
        log.critical('Unrecoverable error in ingest: ' + str(e))


if __name__ == '__main__':

    # Deal with arguments
    args = docopt(__doc__)

    nprocess = int(args['--nprocess'])
    print('ingest_runner with %d processes' % nprocess)

    # Start up the processes
    process_list = []
    for i in range(nprocess):
        p = Process(target=setup_proc, args=(i+1, nprocess, args))
        process_list.append(p)
        p.start()

    for p in process_list:
        p.join()
    print('ingest_runner exiting')
