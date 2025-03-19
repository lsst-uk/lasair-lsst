import json
import prims
# This code reads in Lasair Schema File, loosely based on 
# AVRO schema files (.avsc) and converts it to any of several formats
# required by Lasair

def sql_alter_table(schema_old, schema_new):
    # Build the ALTER TABLE statement for MySQL to create this table
    tablename = schema_old['name']

    fields_old = schema_old['fields'] + schema_old.get('ext_fields', [])
    attr_old = [f['name'] for f in fields_old if 'name' in f]

    fields_new = schema_new['fields'] + schema_new.get('ext_fields', [])
    attr_new = [f['name'] for f in fields_new if 'name' in f]

    lines = ''
    for f in fields_new:
        if not 'name' in f:       continue
        if f['name'] in attr_old: continue
        lines += 'ALTER TABLE %s ADD `%s` %s;\n' % \
                (tablename, f['name'], prims.sql_type(f['type']))
    for f in fields_old:
        if not 'name' in f:       continue
        if f['name'] in attr_new: continue
        lines += 'ALTER TABLE %s DROP COLUMN `%s` %s\n;' % \
                (tablename, f['name'], prims.sql_type(f['type']))
    return lines

def cql_alter_table(schema_old, schema_new):
    # Build the ALTER statement for Cassandra to create this table
    tablename = schema_old['name']

    fields_old = schema_old['fields'] + schema_old.get('ext_fields', [])
    attr_old = [f['name'] for f in fields_old if 'name' in f]

    fields_new = schema_new['fields'] + schema_new.get('ext_fields', [])
    attr_new = [f['name'] for f in fields_new if 'name' in f]

    lines = ''
    for f in fields_new:
        if not 'name' in f:       continue
        if f['name'] in attr_old: continue
        lines += 'ALTER TABLE %s ADD "%s" %s;\n' % \
                (tablename, f['name'], prims.cql_type(f['type']))
    for f in fields_old:
        if not 'name' in f:       continue
        if f['name'] in attr_new: continue
        lines += 'ALTER TABLE %s DROP `%s` %s;\n' % \
                (tablename, f['name'], prims.sql_type(f['type']))
    return lines

import sys
import importlib
if __name__ == '__main__':
    if len(sys.argv) > 4:
        switch         = sys.argv[1]
        schema_ver_old = sys.argv[2]
        schema_ver_new = sys.argv[3]
        table          = sys.argv[4]
    else:
        print("Usage: convert.py switch schema_ver_old schema_ver_new table")
        print("Where switch can be sql or cql")
        print("and schema_version can be for example 704")
        print("and table is one of objects, sherlock_classifications, etc")
        sys.exit()

    schema_package_old = importlib.import_module('%s.%s' % (schema_ver_old, table))
    schema_old = schema_package_old.schema
    schema_package_new = importlib.import_module('%s.%s' % (schema_ver_new, table))
    schema_new = schema_package_new.schema

    if switch == 'sql':
        lines = sql_alter_table(schema_old, schema_new)
    elif switch == 'cql':
        lines = cql_alter_table(schema_old, schema_new)
    else:
        print('Unknown switch %s' % switch)
    if len(lines) > 0:
        print(lines)
