"""
3_make_create_table.py
Build the CREATE TABLE statement for the given table, either SQL or CQL
"""
import json
import prims

# SQL version
def sql_create_table(schema):
    # Build the CREATE TABLE statement for MySQL to create this table
    tablename = schema['name']
    lines = []
    # go through all the fields
    for f in schema['fields'] + schema.get('ext_fields', []):
        if not 'name' in f:
            continue
        s = '`' + f['name'] + '`'       # name with backquotes for SQL
        s += prims.sql_type(f['type'])  # convert AVRO type to SQL type
    
        if 'default' in f:              # is there a DEFAULT
            default = 'NULL'
            if f['default']: default = f['default'] 
            s += ' DEFAULT ' + default

        if 'extra' in f:                # is there an EXTRA
            s += ' ' + f['extra']
        lines.append(s)
    
    sql = 'CREATE TABLE IF NOT EXISTS ' + schema['name'] + '(\n'
    sql += ',\n'.join(lines)

    if 'indexes' in schema:             # add in the INDEX
        sql += ',\n' + ',\n'.join(schema['indexes'])

    sql += '\n)\n'
    return sql

# CQL version
def cql_create_table(schema):
    tablename = schema['name']
    lines = []
    # go through all the fields
    for f in schema['fields']:
        s = '"' + f['name'] + '"'       # name with doublequotes for CQL
        s += prims.cql_type(f['type'])  # convert AVRO type to CQL type
    
        if 'extra' in f:                # is there an EXTRA
            s += ' ' + f['extra']
        lines.append(s)
    
    cql = 'CREATE TABLE IF NOT EXISTS ' + schema['name'] + '(\n'
    cql += ',\n'.join(lines)

    if 'indexes' in schema:             # add in the INDEX
        cql += ',\n' + ',\n'.join(schema['indexes'])

    cql += '\n)\n'

    if 'with' in schema:                # add in the WITH at the very end
        cql += schema['with'] + '\n'

    # 2025-07-24 KWS For some reason execution of CQL files requires a semicolon.
    return cql + ';'

import sys
import importlib
if __name__ == '__main__':
    if len(sys.argv) > 3:
        switch         = sys.argv[1]
        schema_version = sys.argv[2]
        table          = sys.argv[3]
    else:
        print("Usage: 3_make_create_table.py switch schema_version table")
        print("Where switch can be sql or cql")
        print("and schema_verrsion can be for example 704")
        print("and table is one of objects, sherlock_classifications, etc")
        sys.exit()

    schema_package = importlib.import_module('%s.%s' % (schema_version, table))
    schema = schema_package.schema

    if switch == 'sql':
        print(sql_create_table(schema))
    elif switch == 'cql':
        print(cql_create_table(schema))
    else:
        print('Unknown switch %s' % switch)
