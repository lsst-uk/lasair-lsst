# create a dump of just the tables relating to the web frontend

import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
from my_cmd import execute_cmd
today = datetime.today().strftime('%Y%m%d')
now   = datetime.today().strftime('%Y%m%d %H:%M:%S')

logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- mysql backup (web) at %s"' % now
execute_cmd(cmd, logfile)

cmd = f"mysqldump --user={settings.DB_USER_READWRITE} --password={settings.DB_PASS_READWRITE} \
        --port={settings.BACKUP_DATABASE_PORT} --host={settings.BACKUP_DATABASE_HOST} {settings.DB_DATABASE} \
        annotators areas auth_group auth_group_permissions auth_permission auth_user auth_user_groups \
        auth_user_user_permissions authtoken_token django_admin_log django_content_type django_migrations \
        django_session lasair_statistics  mma_areas myqueries users_profile watchlist_cones watchlists \
        > {settings.MYSQL_BACKUP_DIR}/mysqlbackup.sql"
execute_cmd(cmd, logfile)

cmd = 'ls -l %s' % settings.MYSQL_BACKUP_DIR
execute_cmd(cmd, logfile)

