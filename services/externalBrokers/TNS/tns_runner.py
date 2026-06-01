#!/usr/bin/env python
"""Wrapper for the TNS refresher, putting logs where Lasair can see them.

Usage:
  %s [--daysAgo=<n>] [--hourly] [--radius=<f>]
  %s (-h | --help)
  %s --version

Options:
  -h --help            Show this screen.
  --version            Show version.
  --daysAgo=<n>        Which nightly report to fetch. 1 day ago is default.
                       If 'All', then the whole TNS database is scrubbed and rebuilt
  --hourly             Get the TNS data for the current hour.
  --radius=<f>         Matching radius, arcseconds, default 3


E.g.:
  %s --daysAgo=1
  %s --hourly
  %s --hourly --radius=5
"""

import os,sys, time
sys.path.append('../../../common')
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
from gkutils.commonutils import cleanOptions
import settings
from src import date_nid
import datetime
sys.path.append('../../../common/src')
sys.path.append('../..')
from my_cmd import execute_cmd
import slack_webhook
import lasairLogging
from docopt import docopt

def now():
    # current UTC as string
    return datetime.datetime.now(datetime.UTC).strftime("%Y/%m/%dT%H:%M:%S")

if __name__ == "__main__":
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Leave the options as a dict. Easier to handle below.

    slack_channel = getattr(settings, 'SLACK_CHANNEL', None)
    lasairLogging.basicConfig(
        filename='/home/ubuntu/logs/svc.log',
        webhook=slack_webhook.SlackWebhook(url=settings.SLACK_URL, channel=slack_channel),
        merge=True
    )

    log = lasairLogging.getLogger("svc")

    nid  = date_nid.nid_now()
    date = date_nid.nid_to_date(nid)
    logfile = settings.SERVICES_LOG +'/'+ date + '.log'

    cmd = 'echo "\\n-- poll_tns at %s"' % now()
    execute_cmd(cmd, logfile)
    
    arguments = ''
    for k, v in opts.items():
        if v and type(v) is not bool:
            arguments += '--%s=%s ' % (k,v)
        if v and type(v) is bool:
            arguments += '--%s ' % (k)

    cmd = 'python3 poll_tns.py ' + arguments
    execute_cmd(cmd, logfile)
