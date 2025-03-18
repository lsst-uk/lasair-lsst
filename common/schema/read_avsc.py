import requests
import json

def read_from_github(schema_version, component):
    tok = schema_version.split('0')
    major_sv = tok[0]
    minor_sv = tok[1]

    baseUrl = 'https://raw.githubusercontent.com/lsst/alert_packet/refs/heads/main/python/lsst/alert/packet/schema/%s/%s/lsst.v%s_%s.'
    baseUrl = baseUrl % (major_sv, minor_sv, major_sv, minor_sv)

    r = requests.get(baseUrl + component + '.avsc')
    rj = json.loads(r.text)
    rjj = {
        'name': rj['name']+'s',
        'fields':[]
    }
    fields = rj['fields']
    for field in fields:
        # Change the dec to decl
        name = field['name']
        if name == 'dec':
            name = 'decl'

        d = {'name':name}

        # forget the [type, null] possibility, the database defaults missing values to null
        if type(field['type']) == list: d['type'] = field['type'][1]
        else:                           d['type'] = field['type']

        if 'doc' in field: d['doc'] = field['doc']

        rjj['fields'].append(d)
    return rjj

