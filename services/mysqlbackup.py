import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
from my_cmd import execute_cmd
today = datetime.today().strftime('%Y%m%d')
now   = datetime.today().strftime('%Y%m%d %H:%M:%S')

logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- mysql backup at %s"' % now
execute_cmd(cmd, logfile)

cmd = 'mysqldump -u %s -p%s --port=%s --host=%s ztf > %s/mysqlbackup.sql'

cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.BACKUP_DATABASE_PORT, settings.BACKUP_DATABASE_HOST, settings.MYSQL_BACKUP_DIR)
execute_cmd(cmd, logfile)

cmd = 'ls -l %s' % settings.MYSQL_BACKUP_DIR
execute_cmd(cmd, logfile)



