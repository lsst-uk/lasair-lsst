import json
import prims
# This code reads in Lasair Schema File, loosely based on 
# AVRO schema files (.avsc) and converts it to any of several formats
# required by Lasair

def sql_create_table(schema):
    # Build the CREATE TABLE statement for MySQL to create this table
    tablename = schema['name']
    lines = []
    for f in schema['fields'] + schema.get('ext_fields', []):
        if not 'name' in f:
            continue
        s = '`' + f['name'] + '`'
        s += prims.sql_type(f['type'])
    
        if 'default' in f:
            default = 'NULL'
            if f['default']: default = f['default'] 
            s += ' DEFAULT ' + default

        if 'extra' in f:
            s += ' ' + f['extra']
        lines.append(s)
    #    if 'doc'     in f and f['doc']:     s += ', ' + f['doc']
    
    sql = 'CREATE TABLE IF NOT EXISTS ' + schema['name'] + '(\n'
    sql += ',\n'.join(lines)

    if 'indexes' in schema:
        sql += ',\n' + ',\n'.join(schema['indexes'])

    sql += '\n)\n'
    return sql

def cql_create_table(schema):
    # Build the CREATE TABLE statement for Cassandra to create this table
    tablename = schema['name']
    lines = []
    for f in schema['fields']:
        s = '"' + f['name'] + '"'
        s += prims.cql_type(f['type'])
    
        if 'extra' in f:
            s += ' ' + f['extra']
        lines.append(s)
    #    if 'doc'     in f and f['doc']:     s += ', ' + f['doc']
    
    cql = 'CREATE TABLE IF NOT EXISTS ' + schema['name'] + '(\n'
    cql += ',\n'.join(lines)

    if 'indexes' in schema:
        cql += ',\n' + ',\n'.join(schema['indexes'])

    cql += '\n)\n'

    if 'with' in schema:
        cql += schema['with'] + '\n'
    return cql

import sys
import importlib
if __name__ == '__main__':
    if len(sys.argv) > 3:
        switch         = sys.argv[1]
        schema_version = sys.argv[2]
        table          = sys.argv[3]
    else:
        print("Usage: convert.py switch schema_version table")
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
