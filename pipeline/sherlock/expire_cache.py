"""Utility to expire old cache entries. Expected to be run as a cron job.

Usage:
    expire_cache.py --database=URL --max_entries=MAX
    expire_cache.py --database=URL --max_days=MAX
    expire_cache.py --database=URL --min_version=VER

Options:
    --database=URL       Cache database (e.g. mysql://user:pw@host:3306/database)
    --max_entries=MAX    Delete all entries in excess of MAX, oldest first
    --max_days=DAYS      Delete all entries older than DAYS
    --min_version=VER    Delete all entries with a version less than VER
"""

from docopt import docopt
from packaging.version import Version
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
import pymysql.cursors


def main(args):
    url = urlparse(args['--database'])
    connection = pymysql.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        db=url.path.lstrip('/'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    with (connection.cursor() as cursor):
        if args.get('--max_entries'):
            n = args['--max_entries']
            print(f"trimming cache to {n} entries")
            # get the nth entry
            sql = f"SELECT * FROM cache ORDER BY updated DESC LIMIT 1 OFFSET {n-1}"
            cursor.execute(sql)
            row = cursor.fetchone()
            if not row:
                # cache is smaller than n
                print(f"deleted 0 record(s)")
                return
            cutoff = row['updated']
            sql = f"DELETE FROM cache WHERE updated < '{cutoff}'"
            cursor.execute(sql)
            print(f"deleted {cursor.rowcount} record(s)")
        elif args.get('--max_days'):
            n = args['--max_days']
            print(f"trimming cache to {n} days")
            cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=n)).strftime('%Y-%m-%d %H:%M:%S')
            sql = f"DELETE FROM cache WHERE updated < '{cutoff}'"
            cursor.execute(sql)
            print(f"deleted {cursor.rowcount} record(s)")
        elif args.get('--min_version'):
            min_ver = Version(args['--min_version'])
            print(f"removing cache entries for versions prior to {min_ver}")
            # get a list of versions
            sql = f"SELECT DISTINCT version FROM cache"
            cursor.execute(sql)
            old_vers = []
            for row in cursor.fetchall():
                ver = Version(row['version'])
                if ver < min_ver:
                    old_vers.append(f"'{str(ver)}'")
            if len(old_vers) == 0:
                # nothing to do
                print(f"deleted 0 record(s)")
                return
            sql = f"DELETE FROM cache WHERE version IN ({','.join(old_vers)})"
            cursor.execute(sql)
            print(f"deleted {cursor.rowcount} record(s)")


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)