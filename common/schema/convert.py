import json
# This code reads in Lasair Schema File, loosely based on 
# AVRO schema files (.avsc) and converts it to any of several formats
# required by Lasair

def sql_create_table(schema):
    # Build the CREATE TABLE statement for MySQL to create this table
    tablename = schema['name']
    lines = []
    for f in schema['fields']:
        s = '`' + f['name'] + '`'
        primtype = ''
        if 'type'    in f: 
            t = f['type']
            primtype = t
            if isinstance(t, list) and len(t) == 2 and t[1] == 'null':
                primtype = t[0]
        if   primtype == 'float':    s += ' float'
        elif primtype == 'double':   s += ' double'
        elif primtype == 'int':      s += ' int'             # 31 bit with sign
        elif primtype == 'long':     s += ' bigint'          # 63 bit with sign
        elif primtype == 'bigint':   s += ' bigint'          # 63 bit with sign
        elif primtype == 'date':     s += ' datetime(6)'
        elif primtype == 'string':   s += ' varchar(16)'
        elif primtype == 'bigstring':s += ' varchar(80)'
        elif primtype == 'text':     s += ' text'
        elif primtype == 'timestamp':s += ' timestamp'
        elif primtype == 'JSON':     s += ' JSON'
        else: print('ERROR unknown type ', primtype)
    
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
        primtype = ''
        if 'type'    in f: 
            t = f['type']
            primtype = t
            if isinstance(t, list) and len(t) == 2 and t[1] == 'null':
                primtype = t[0]
        if   primtype == 'float':    s += ' float'
        elif primtype == 'double':   s += ' double'
        elif primtype == 'int':      s += ' int'             # 31 bit with sign
        elif primtype == 'long':     s += ' bigint'          # 63 bit with sign
        elif primtype == 'bigint':   s += ' bigint'          # 63 bit with sign
        elif primtype == 'string':   s += ' ascii'
        elif primtype == 'char':     s += ' ascii'
        elif primtype == 'boolean':  s += ' boolean'
        elif primtype == 'blob':     s += ' blob'
        else: print('ERROR unknown type ', primtype)
    
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
    if len(sys.argv) > 2:
        switch = sys.argv[1]
        table = sys.argv[2]
    else:
        print("Usage: convert.py switch table")
        print("Where switch can be sql or cql")
        print("and table is one of objects, sherlock_classifications, etc")
        sys.exit()

    schema_package = importlib.import_module('lasair_schema.' + table)
    schema = schema_package.schema

    out = open('lasair_%s/%s.%s' % (switch, table, switch), 'w')

    if switch == 'sql':
        out.write(sql_create_table(schema))
    elif switch == 'cql':
        out.write(cql_create_table(schema))
    else:
        print('Unknown switch %s' % switch)
    out.close()
