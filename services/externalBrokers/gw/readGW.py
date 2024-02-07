import os, sys, json
import yaml
from yaml import CLoader as Loader, CDumper as Dumper


def makeMmaWatchmap(datadir):
    try:
        f = open(datadir + '/meta.yaml')
    except:
        print('no meta.yaml', datadir + '/meta.yaml')
        return ''

    try:
        data = yaml.load(f, Loader=Loader)
    except:
        print('can open meta.yaml but not read it')
        return ''

    try:
        params = {'classification': data['ALERT']['event']['classification']}
    
        area10 = data['EXTRA']['area10']
        area50 = data['EXTRA']['area50']
        area90 = data['EXTRA']['area90']
    
        radec = data['EXTRA']['central coordinate']['equatorial'].split()
    
        loc = {
            'RA'      :float(radec[0].strip()), 
            'Dec'     :float(radec[1].strip()), 
            'mjdObs'  :data['HEADER']['MJD-OBS'], 
            'distmean':data['HEADER']['DISTMEAN'], 
            'diststd' :data['HEADER']['DISTSTD']
            }
        params['location'] = loc
    except Exception as e:
        print(e)
        return ''
    
    jparams = json.dumps(params)
    query = "INSERT INTO MmaWatchmap (area10, area50, area90, params) VALUES (%f, %f, %f, '%s')"
    query = query % (area10, area50, area90, jparams)
    return query

def handle_event(event_dir):
    for release in os.listdir(event_dir):
        if release.startswith('20'):
            print(event_dir, release)
            query = makeMmaWatchmap(event_dir + release)
            print(query)

############
dir = '/home/ubuntu/o4_events/superevents/_high_significance/'
for file in os.listdir(dir):
    if file.startswith('S'):
        handle_event(dir + file + '/')
