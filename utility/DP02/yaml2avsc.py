import json, sys
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

def fix_type(typ):
    if typ == 'char': return 'string'
    else: return typ

def table_schema(table):
    fields = []
    for column in table['columns']:
        field = {
            'name':column['name'], 
            'type': ['null', fix_type(column['datatype'])], 
            'doc':column['description'],
        }
        fields.append(field)

    schema = {
        "name": table['name'],
        "type": ['null', {
            "type": "record",
            "name": table['name'],
            "fields": fields,
        }]
    }
    return schema

def get_table(tables, table_name):
    for table in tables:
#        print(table['name'])
        if table['name'] == table_name:
            return table_schema(table)
    print('ERROR: table %s not found' % table_name)


#######

schema = {
    "name": "DP0.2",
    "type": "record",
    "fields": [ ]
}

data = load(sys.stdin, Loader=Loader)
tables = data['tables']

s = get_table(tables, 'DiaObject')
schema['fields'].append(s)

s = get_table(tables, 'DiaSource')
schema['fields'].append(s)
s = {
  "name": "DiaSourceList",
  "type": [ "null", { "type": "array", "items": "DiaSource" } ]
  }
schema['fields'].append(s)

s = get_table(tables, 'ForcedSourceOnDiaObject')
schema['fields'].append(s)
s = {
  "name": "ForcedSourceOnDiaObjectList",
  "type": [ "null", { "type": "array", "items": "ForcedSourceOnDiaObject" } ]
  }
schema['fields'].append(s)

print(json.dumps(schema, indent=2))
