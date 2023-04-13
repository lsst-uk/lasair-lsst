import sys
sys.path.append('../common')
import settings
sys.path.append('../common/src')

import slack_webhook
import lasairLogging

from subprocess import Popen, PIPE



def execute_cmd(cmd, logfile=None):
    """ Executes a command like os.system, puts stdout into the log file
    and writes to slack if exception as well as non-zero return code
    """

    process = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
    out, err = process.communicate()
    out = out.decode('utf8')
    err = err.decode('utf8')
    log = lasairLogging.getLogger("svc")

    if logfile:
        try:
            f = open(logfile, 'a')
        except:
            log.error("ERROR: Cannot open system logfile %s:%s" % (logfile, str(e)))
        f.write(out)
        f.close
    else:
        print('%s' % out)

    if len(err) > 0:
        log.error("ERROR: %s" % err)

    return process.returncode


if __name__ == "__main__":
    lasairLogging.basicConfig(
        filename='/home/ubuntu/logs/svc.log',
        webhook=slack_webhook.SlackWebhook(url=settings.SLACK_URL),
        merge=True
    )

    log = lasairLogging.getLogger("svc")

    # run smoothly
    cmd = 'ls -l /mnt/cephfs/lasair'
    ret = execute_cmd(cmd, 'junk')
    print('returns ', ret)

    # will cause error
    cmd = 'ls -l /mnt/nosuchdirectory'
    ret = execute_cmd(cmd, 'junk')
    print('returns ', ret)
