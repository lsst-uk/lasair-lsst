import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
from my_cmd import execute_cmd
today = datetime.today().strftime('%Y%m%d')
now   = datetime.today().strftime('%Y%m%d %H:%M:%S')

logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- dump annotations master at %s"' % now
execute_cmd(cmd, logfile)

if not os.path.exists(settings.ANNOTATIONS_DUMP):
    os.makedirs(settings.ANNOTATIONS_DUMP)

cmd = 'mysqldump -u %s -p%s --port=%s --host=%s ztf annotations > %s/annotations.sql'
cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_PORT, settings.DB_HOST, settings.ANNOTATIONS_DUMP)
execute_cmd(cmd, logfile)

cmd = 'mysql -u %s -p%s --port=%s --host=%s ztf -e "select count(*) from annotations"'
cmd = cmd % (settings.DB_USER_READONLY, settings.DB_PASS_READONLY, settings.DB_PORT, settings.DB_HOST)
execute_cmd(cmd, logfile)

cmd = 'ls -l %s/annotations.sql' % settings.ANNOTATIONS_DUMP
execute_cmd(cmd, logfile)
