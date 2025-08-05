"""Check Object Database Schema

Validate the schema used in the object database against the JSON version of the schema in git.
Raises an AssertionError and returns with non-zero if the number of fields or names of fields
differ (types are not checked).
"""

import sys
import json
import mysql.connector
import requests
import argparse
import re
from importlib import import_module

sys.path.append('../common')

def get_mysql_names(conf):
    config = {
      'user': conf['user'], 
      'password': conf['password'], 
      'host': conf['host'], 
      'port': conf['port'], 
      'database': conf['database'], 
      }
    msl = mysql.connector.connect(**config)

    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'describe objects'
    cursor.execute(query)
    mysql_names = []
    for row in cursor:
        mysql_names.append(row['Field'])
    return mysql_names

def get_schema_names(conf):
    global schema_package
    schema_names = []
    if conf['url']:
        schema_text = requests.get(conf['url']).text
        # if schema format is python then convert to json first
        if conf['format'] == 'py':
            schema_text = re.sub("^.*{", "{", schema_text, count=1)
            schema_text = re.sub("#.*", "", schema_text)
        schema = json.loads(schema_text)
    else:
        schema = schema_package.schema
    for field in schema['fields'] + schema['ext_fields']:
        if 'name' in field:
            schema_names.append(field['name'])
    return schema_names

if __name__ == "__main__":
    # parse cmd line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', default='ztf', type=str, help='MySQL username')
    parser.add_argument('--password', type=str, help='MySQL password')
    parser.add_argument('--host', type=str, help='MySQL hostname')
    parser.add_argument('--port', type=int, default=3306, help='MySQL port number')
    parser.add_argument('--database', type=str, default='ztf', help='Name of database')
    parser.add_argument('--format', type=str, default='py', help='Schema format (json|py)')
    parser.add_argument('--mod', type=str, help='module to import the schema from')
    parser.add_argument('--url', type=str, help='URL to get the schema from')
    conf = vars(parser.parse_args())

    if not bool(conf['mod']) ^ bool(conf['url']):
        print("Please specify exactly one of -mod and --url")
        sys.exit()

    if conf['mod']:
        schema_package = import_module('schema.' + conf['mod'])

    schema_names = get_schema_names(conf)
    mysql_names = get_mysql_names(conf)

    assert len(mysql_names) == len(schema_names), "Schema validation failed: different length"

    for i in range(len(mysql_names)):
        assert mysql_names.sort() == schema_names.sort(), "Schema validation failed: {} != {}".format(mysql_names, schema_names)

    print('mysql and object schema identical')

