import sys
sys.path.append('../../common/src')
import logging
import json
from multiprocessing import Process, connection
from time import sleep
from multiprocessing_logging import install_mp_handler
import slack_webhook

# default config file location
conffile = "wrapper_runner.json"

class SlackHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        try:
            slack_webhook.send(settings['slack_url'], log_entry)
        except Exception as e:
            print ("Error sending Slack message")
            print (repr(e))

def run(log, process):
    if process % 2 == 0:
        print(f"foo{process} err")
        return "1"
    for i in range(4):
        log.info(f"foo{process} {i}")
        print(f"foo{process} {i}")
        sleep(1)

if __name__ == '__main__':
    with open(conffile) as file:
        settings = json.load(file)
    n = settings.get('procs', 1)
    delay = settings.get('delay', 2)
    max_restarts = settings.get('max_restarts', 10)

    logformat = f"%(asctime)s:%(levelname)s:%(processName)s:%(funcName)s:%(message)s"
    logging.basicConfig(format=logformat, level=logging.DEBUG)
    log = logging.getLogger("mptest")
    install_mp_handler()
    log.addHandler(SlackHandler(level=logging.ERROR))

    procs = []
    sentinels = []
    i = 0
    while True:
        # if number of processes < desired then start another one
        if len(procs) < n:
            log.info(f"Starting wrapper process {i}")
            p = Process(target=run, args=(log,i))
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
                        procs.remove(p)
                        p.close()
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

