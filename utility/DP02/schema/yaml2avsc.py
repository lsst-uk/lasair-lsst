import json, sys
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

def table_schema(table):
    fields = []
    for column in table['columns']:
        field = {
            'name':column['name'], 
            'type':column['datatype'], 
            'doc':column['description'],
        }
        fields.append(field)

    schema = {
        "name": table['name'],
        "type": {
            "type": "record",
            "name": "DP02_" + table['name'],
            "fields": fields,
        }
    }
    return schema

def get_table(tables, table_name):
    for table in tables:
#        print(table['name'])
        if table['name'] == table_name:
            return table_schema(table)


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
  "name": "DiaSourcesList",
  "type": [ "null", { "type": "array", "items": "DiaSource" } ]
  }
schema['fields'].append(s)

s = get_table(tables, 'ForcedSourceOnDiaObject')
schema['fields'].append(s)

s = {
  "name": "ForcedSourceOnDiaObjectsList",
  "type": [ "null", { "type": "array", "items": "ForcedSourceOnDiaObject" } ]
  }
schema['fields'].append(s)

print(json.dumps(schema, indent=2))
