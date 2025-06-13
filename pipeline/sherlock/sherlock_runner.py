"""
Sherlock wrapper proess runner. Takes the --nprocess arg and starts that many processes,
with other arguments sent there, also logs the outputs. 
If maxalert is specified, it does that many for each process then exits,
otherwise maxalert is the largest possible. 
SIGTERM is passed to those children and dealt with properly.
Usage:
    sherlock_wrapper.py [--nprocess=nprocess]
              [--config=FILE]

Options:
    --nprocess=nprocess  Number of processes [default: 1]
    --config=FILE        Configuration file [default: wrapper_runner.json]
"""
import os
import sys
import json
import yaml
import signal
from docopt import docopt
from multiprocessing import Process, Value, Array

sys.path.append('../../common/src')
import slack_webhook
import lasairLogging
import wrapper


def setup_proc(exit_code, pids, n, nprocess, conffile):
    print('test')
    # Load runner config
    with open(conffile) as file:
        config = json.load(file)

    # Load wrapper config
    conf = {}
    with open(config.get('wrapper_conf_file', 'wrapper_config.yaml'), "r") as f:
        cfg = yaml.safe_load(f)
        for key, value in cfg.items():
            conf[key] = value

    # Set up the logger
    lasairLogging.basicConfig(
        filename=f"/home/ubuntu/logs/sherlock_wrapper-{n}.log",
        webhook=slack_webhook.SlackWebhook(url=config.get('slack_url', '')),
        merge=True
    )
    log = lasairLogging.getLogger("sherlock_runner")

    log.info(f"Starting sherlock runner process {n} of {nprocess}")
    try:
        wrapper.run(conf, log)
    except Exception as e:
        log.exception('Exception')
        log.critical('Unrecoverable error in sherlock: ' + str(e))
        # set the exit code
        exit_code.value = 1
        # send a SIGTERM to all other processes
        for pid in pids:
            if pid != os.getpid() and pid > 0:
                print("Sending SIGTERM to", pid)
                os.kill(pid, signal.SIGTERM)


def main():
    # Deal with arguments
    args = docopt(__doc__)

    nprocess = int(args.get('--nprocess'))
    print('sherlock_runner with %d processes' % nprocess, flush=True)

    conffile = args.get('--config')

    exit_code = Value('i', 0)
    pids = Array('i', nprocess)

    # Start up the processes
    process_list = []
    for i in range(nprocess):
        p = Process(target=setup_proc, args=(exit_code, pids, i+1, nprocess, conffile))
        process_list.append(p)
        p.start()
        pids[i] = p.pid

    for p in process_list:
        p.join()

    print("sherlock_runner exiting with exit code", exit_code.value)
    return exit_code.value


if __name__ == '__main__':
    retval = main()
    sys.exit(retval)
