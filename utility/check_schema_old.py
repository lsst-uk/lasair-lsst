"""
Check Database Schema
Validate the schema used in the object database against the .py 
version of the schema in git.
Raises an AssertionError and returns with non-zero if the 
number of fields or names of fields differ (types are not checked).

Usage:
    check_schema.py [--local|--main] <schema_name>

Options:
    --local    Checks the schema of the given schema_name in the local database
    --main     Checks in the main database (default)
"""

import sys
sys.path.append('../common')
from src import db_connect
import importlib
from docopt import docopt

def get_mysql_attrs(msl):

    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'describe objects'
    cursor.execute(query)
    mysql_attrs = []
    for row in cursor:
        mysql_attrs.append(row['Field'])
    return mysql_attrs

if __name__ == "__main__":
    args = docopt(__doc__)
    schema_name = args['<schema_name>']

    schema_attrs = []
    schema_package = importlib.import_module('schema.' + schema_name)
    schema = schema_package.schema
    for field in schema['fields']:
        schema_attrs.append(field['name'])

    if args['--local']:
        msl = db_connect.local()
    else:
        msl = db_connect.readonly()
    mysql_attrs = get_mysql_attrs(msl)

    assert len(mysql_attrs) == len(schema_attrs), "Schema validation failed: different length"

    for i in range(len(mysql_attrs)):
        assert mysql_attrs[i] == schema_attrs[i], "Schema validation failed: {} != {}".format(mysql_attrs[i], schema_attrs[i])

    print('mysql and object schema identical')
