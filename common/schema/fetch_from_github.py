import requests, json
baseUrl = 'https://raw.githubusercontent.com/lsst/alert_packet/refs/heads/main/python/lsst/alert/packet/schema/7/2/lsst.v7_2.'

indexes = {
    'diaForcedSource'     :'PRIMARY KEY ("diaObjectId","midpointMjdTai")', 
    'diaNondetectionLimit':'PRIMARY KEY ("midpointMjdTai")', 
    'diaObject'           :'PRIMARY KEY ("diaObjectId")', 
    'diaSource'           :'PRIMARY KEY ("diaObjectId", "midpointMjdTai", "diaSourceId")', 
    'ssObject'            :'PRIMARY KEY ("ssObjectId")',
}

for q,index in indexes.items():
    print(q)
    r = requests.get(baseUrl + q + '.avsc')
    rj = json.loads(r.text)
    rjj = {
        'name': rj['name']+'s', 
        'fields':[]
    }
    fields = rj['fields']
    for field in fields:
        d = {'name':field['name']}

        if type(field['type']) == list: d['type'] = field['type'][1]
        else:                           d['type'] = field['type']

        if 'doc' in field: d['doc'] = field['doc']

        rjj['fields'].append(d)
    s = "schema = {\n  'indexes':['%s']," % index
    s += json.dumps(rjj, indent=2)[1:]
    f = open('lsst_schema/' + q + 's.py', 'w')
    f.write(s)
    f.close()


