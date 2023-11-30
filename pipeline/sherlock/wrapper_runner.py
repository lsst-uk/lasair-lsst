import sys
sys.path.append('../../common/src')
import logging
import json
import yaml
from multiprocessing import Process, connection
from time import sleep
from multiprocessing_logging import install_mp_handler
import slack_webhook
import wrapper
import lasairLogging

# default config file location
conffile = "wrapper_runner.json"

if __name__ == '__main__':
    with open(conffile) as file:
        settings = json.load(file)
    n = settings.get('procs', 1)
    delay = settings.get('delay', 2)
    max_restarts = settings.get('max_restarts', 10)
    wrapper_conf_file = settings.get('wrapper_conf_file', 'wrapper_config.yaml')
    slack_url = settings.get('slack_url', '')

    conf = {}
    with open(wrapper_conf_file, "r") as f:
        cfg = yaml.safe_load(f)
        for key,value in cfg.items():
            conf[key] = value

    logformat = f"%(asctime)s:%(levelname)s:%(processName)s:%(funcName)s:%(message)s"
    lasairLogging.basicConfig(
        filename='/home/ubuntu/wrapper.log',
        webhook=slack_webhook.SlackWebhook(url=slack_url),
        merge=True
    )
    log = lasairLogging.getLogger("wrapper_runner")
    install_mp_handler()

    procs = []
    sentinels = []
    i = 0
    while True:
        # if number of processes < desired then start another one
        if len(procs) < n:
            log.info(f"Starting wrapper process {i}")
            p = Process(target=wrapper.run, args=(conf, log))
            procs.append(p)
            p.start()
            sentinels.append(p.sentinel)
            i += 1
        # if desired number of processes then wait for one to finish
        else:
            log.debug("Waiting on wrapper process")
            # when a sentinel indicaates a process has ended, remove process and sentinel from lists
            for s in connection.wait(sentinels):
                log.info(f"Wrapper process ended")
                sentinels.remove(s)
                for p in procs:
                    if p.sentinel == s:
                        p.join()
                        p.close()
                        procs.remove(p)
            if i >= n:
                if i - n >= max_restarts:
                    log.info(f"Max restarts exceeded, giving up")
                    break
                log.info(f"Sleeping for {delay}s")
                sleep(delay)

    log.debug("Terminating remaining processes")
    for p in procs:
        p.terminate()
    log.debug("Waiting for remaining processes to terminate")
    for p in procs:
        p.join()
        p.close()

    log.info("Wrapper runner exiting")

