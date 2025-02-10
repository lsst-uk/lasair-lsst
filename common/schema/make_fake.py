import sys
import json
import random
import lsst_schema.diaObjects       as diaO
import lsst_schema.diaSources       as diaS
import lsst_schema.diaForcedSources as diaF
import lsst_schema.ssObjects        as ssO

def make_fake_value(field):
    if not 'name' in field:
        return None
    n = field['name']
    t = field['type']
    if t == 'float' or t == 'double':
        v = random.random()
    elif t == 'int' or t == 'long':
        v = random.randrange(1000)
    elif t == 'string':
        v = 'hello'
    elif t == 'boolean':
        v = random.choice([True, False])
    elif n == 'htm16' or n == 'timestamp':
        return None
    else:
        print('Name %s of unknown type %s' % (n, t))
        return None
    return v

def make_alert():
    diaObject = {}
    for field in diaO.schema['fields']:
        v = make_fake_value(field)
        if v: diaObject[field['name']] = v
    
    ssObject = {}
    for field in ssO.schema['fields']:
        v = make_fake_value(field)
        if v: ssObject[field['name']] = v
    
    ndiaS = random.randrange(1, 10)
    prvDiaSources = []
    for i in range(ndiaS):
        diaSource = {}
        for field in diaS.schema['fields']:
            v = make_fake_value(field)
            if v: diaSource[field['name']] = v
        if i < ndiaS-1:   # last one stands by itself
            prvDiaSources.append(diaSource)
    
    ndiaF = random.randrange(0, 10)
    prvDiaForcedSources = []
    for i in range(ndiaF):
        diaForcedSource = {}
        for field in diaF.schema['fields']:
            v = make_fake_value(field)
            if v: diaForcedSource[field['name']] = v
        prvDiaForcedSources.append(diaForcedSource)
    
    alertId = random.randrange(100000)
    alert = {
        'alertId':             alertId,
        'diaObject':           diaObject,
        'diaSource':           diaSource,
        'prvDiaSources':       prvDiaSources,
        'prvDiaForcedSources': prvDiaForcedSources,
        'ssObject':            ssObject,
    }
    return alert
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        dir = sys.argv[1]
        n = int(sys.argv[2])
    else:
        print('Usage: make_fake <directory> <number>')
        sys.exit()

    for i in range(n):
        alert = make_alert()
        alertId = alert['alertId']
        f = open('%s/file%05d.json' % (dir, alertId), 'w')
        f.write(json.dumps(alert, indent=2))
        f.close()
