import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
from my_cmd import execute_cmd
today = datetime.today().strftime('%Y%m%d')
now   = datetime.today().strftime('%Y%m%d %H:%M:%S')

logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- dump crossmatch_tns master at %s"' % now
execute_cmd(cmd, logfile)

if not os.path.exists(settings.CROSSMATCH_TNS_DUMP):
    os.makedirs(settings.CROSSMATCH_TNS_DUMP)

cmd = 'mysqldump -u %s -p%s --port=%s --host=%s ztf crossmatch_tns > %s/crossmatch_tns.sql'
cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_PORT, settings.DB_HOST, settings.CROSSMATCH_TNS_DUMP)
execute_cmd(cmd, logfile)

cmd = 'mysql -u %s -p%s --port=%s --host=%s ztf -e "select count(*) from crossmatch_tns"'
cmd = cmd % (settings.DB_USER_READONLY, settings.DB_PASS_READONLY, settings.DB_PORT, settings.DB_HOST)
execute_cmd(cmd, logfile)

cmd = 'ls -l %s/crossmatch_tns.sql' % settings.CROSSMATCH_TNS_DUMP
execute_cmd(cmd, logfile)
