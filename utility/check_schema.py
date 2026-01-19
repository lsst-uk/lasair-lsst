"""Check Object Database Schema

Validate the schema used in the object database against the JSON version of the schema in git.
Raises an AssertionError and returns with non-zero if the number of fields or names of fields
differ (types are not checked).

Usage:
  check_schema.py [--user=<user>] [--password=<pwd>] [--host=<host>] [--port=<port>] [--database=<db>]
                  [--format=<fmt>] (--mod=<mod> | --url=<url>) [--cassandra]
  check_schema.py (-h | --help)

Options:
  -h --help                    Show this help message.
  --user=<user>                MySQL username [default: ztf].
  --password=<pwd>             MySQL password.
  --host=<host>                MySQL hostname or Cassandra contact point.
  --port=<port>                MySQL or Cassandra port number [default: 3306].
  --database=<db>              Name of database or Cassandra keyspace [default: ztf].
  --format=<fmt>               Schema format (json|py) [default: py].
  --mod=<mod>                  Module to import the schema from.
  --url=<url>                  URL to get the schema from.
  --cassandra                  Do a schema check against cassandra, not MySQL.

E.g.
  python %s --user=dbuser --password=dbpass --host=localhost --port=3306 --database=dbname --mod=9_0_A.objects
  python %s --host=localhost --port=9042 --database=lasair --cassandra --mod=9_0_A.diaObjects

  python %s --user=dbuser --password=dbpass --host=localhost --port=3306 --database=dbname --url=https://raw.githubusercontent.com/lsst-uk/lasair-lsst/refs/heads/develop/common/schema/9_0_A/objects.py
  python %s --host=localhost --port=9042 --database=lasair --cassandra --url=https://raw.githubusercontent.com/lsst-uk/lasair-lsst/refs/heads/develop/common/schema/9_0_A/diaObjects.py
"""

import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
import json
import mysql.connector
import requests
import re
from importlib import import_module
from docopt import docopt
import yaml

sys.path.append('../common')

def get_mysql_names(conf):
    """Get column names (and types) from MySQL

    Args:
        conf (dict): The config settings

    Returns:
        dict: A dictionary of columns and types
    """

    config = {
      'user': conf['user'],
      'password': conf['password'],
      'host': conf['host'],
      'port': int(conf['port']),
      'database': conf['database'],
    }
    if conf['mod']:
        table = conf['mod'].split('.')[-1]
    else:
        table = conf['url'].split('/')[-1].split('.')[-2]

    msl = mysql.connector.connect(**config)
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute("select column_name, column_type from information_schema.columns where table_name=%s", (table,))
    mysql_names = [row['column_name'] for row in cursor]
    return mysql_names


def get_cassandra_names(conf):
    """Get column names (and types) from Cassandra

    Args:
        conf (dict): The config settings

    Returns:
        dict: A dictionary of columns and types
    """

    from cassandra.cluster import Cluster
    from cassandra.query import dict_factory

    if conf['mod']:
        table = conf['mod'].split('.')[-1].lower()
    else:
        table = conf['url'].split('/')[-1].split('.')[-2].lower()

    print("TABLE =", table)

    cluster = Cluster([conf['host']], port=int(conf['port']))
    session = cluster.connect()
    session.row_factory = dict_factory

    query = """
      SELECT column_name, type
      FROM system_schema.columns
      WHERE keyspace_name=%s AND table_name=%s;
    """
    rows = session.execute(query, (conf['database'], table))
    cassandra_names = [row['column_name'] for row in rows]
    return cassandra_names


def get_schema_names(conf):
    """Get the schema information from a (mod) or remote (url) python file

    Args:
        conf (dict): The config settings

    Returns:
        dict: A dictionary of columns and types
    """

    global schema_package
    schema_names = []
    if conf['url']:
        schema_text = requests.get(conf['url']).text
        if conf['format'] == 'py':
            schema_text = re.sub("^.*{", "{", schema_text, count=1)
            schema_text = re.sub("#.*", "", schema_text)
            # 2025-11-25 KWS The "with" key for cutouts has multi-line triple quotes. Can't read this
            #                with YAML or JSON. So get rid of it.
            schema_text = re.sub(r'"with"\s*:\s*""".*?"""','"with": ""',schema_text,flags=re.DOTALL)

        # 2025-11-25 KWS Use YAML, not JSON, since the 'indexes' key in Cassandra objects is not valid JSON.
        #                YAML will read it OK, since it is more forgiving.
        schema = yaml.safe_load(schema_text)
        schema.pop("with", None) 
    else:
        schema = schema_package.schema
    try:
        fields = schema['fields'] + schema['ext_fields']
    except KeyError as e:
        fields = schema['fields']

    for field in fields:
        if 'name' in field:
            schema_names.append(field['name'])
    return schema_names


if __name__ == "__main__":
    args = docopt(__doc__)

    conf = {
        'user': args['--user'],
        'password': args['--password'],
        'host': args['--host'],
        'port': args['--port'],
        'database': args['--database'],
        'format': args['--format'],
        'mod': args['--mod'],
        'url': args['--url'],
        'cassandra': args['--cassandra'],
    }

    if not bool(conf['mod']) ^ bool(conf['url']):
        print("Please specify exactly one of --mod or --url")
        sys.exit(1)

    if conf['mod']:
        schema_package = import_module('schema.' + conf['mod'])

    schema_names = get_schema_names(conf)

    if conf['cassandra']:
        database_names = get_cassandra_names(conf)
    else:
        database_names = get_mysql_names(conf)

    for mname in database_names:
        if mname not in schema_names:
            print(mname, 'in backend database but not in schema')
    for sname in schema_names:
        if sname not in database_names:
            print(sname, 'in schema but not in backend database')

    assert len(database_names) == len(schema_names), "Schema validation failed: different length"

    database_names.sort()
    schema_names.sort()
    assert database_names == schema_names, f"Schema validation failed: {database_names} != {schema_names}"

    print('Backend database and object schema are identical')
