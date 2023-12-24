#!/usr/bin/env python
"""
Run the TNS refresher, putting logs where Lasair can see them
"""

import os,sys, time
sys.path.append('../../../common')
import settings
from src import date_nid
from datetime import datetime
sys.path.append('../../../common/src')
sys.path.append('../..')
from my_cmd import execute_cmd
import slack_webhook
import lasairLogging

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

if __name__ == "__main__":
    lasairLogging.basicConfig(
        filename='/home/ubuntu/logs/svc.log',
        webhook=slack_webhook.SlackWebhook(url=settings.SLACK_URL),
        merge=True
    )

    log = lasairLogging.getLogger("svc")

    nid  = date_nid.nid_now()
    date = date_nid.nid_to_date(nid)
    logfile = settings.SERVICES_LOG +'/'+ date + '.log'

    cmd = 'echo "\\n-- poll_tns at %s"' % now()
    execute_cmd(cmd, logfile)

    cmd = 'python3 poll_tns.py --daysAgo=1'
    execute_cmd(cmd, logfile)
