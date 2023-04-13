import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
from my_cmd import execute_cmd
today = datetime.today().strftime('%Y%m%d')
now   = datetime.today().strftime('%Y%m%d %H:%M:%S')
logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- fetch annotations at %s"' % now
execute_cmd(cmd, logfile)

cmd = 'mysql -u ztf -p ztf -p%s < %s/annotations.sql'
cmd = cmd % (settings.LOCAL_DB_PASS, settings.ANNOTATIONS_DUMP)
execute_cmd(cmd, logfile)

cmd = 'mysql -u ztf -p%s ztf -e "select count(*) from annotations"'
cmd = cmd % settings.LOCAL_DB_PASS
execute_cmd(cmd, logfile)
