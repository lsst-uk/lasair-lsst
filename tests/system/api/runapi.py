"""
Run Lasair API test suite using both GET and POST and Python.
"""

import json
import os
import sys
import lasair
import urllib.parse
sys.path.append('../../../common')

try:
    import settings
except:
    pass

out_file = 'tmp.json'

def lenornothing(w):
    try:
        return str(len(w))
    except:
        return 'NOTHING'

def curltest(input, method, verbose):
    try:
        os.remove(out_file)
    except FileNotFoundError:
        pass
    arglist = []
    for k, v in input.items():
        arglist.append('%s=%s' % (k, v))
    cmd = "curl --no-progress-meter -f -o %s " % out_file
    cmd += "--header 'Authorization: Token %s' " % token
    cmd += "--data '%s' " % '&'.join(arglist)
    cmd += "%s/%s/" % (endpoint, method)
    if verbose:
        print('** curl test of %s' % method )
        print(cmd)
    os.system(cmd)
    try:
        computed = open(out_file).read()
        return json.loads(computed)
    except:
        return None


def gettest(input, method, verbose):
    try:
        os.remove(out_file)
    except FileNotFoundError:
        pass
    arglist = []
    for k, v in input.items():
        print(k, v)
        arglist.append('%s=%s' % (k, urllib.parse.quote(str(v))))
    cmd = "curl --no-progress-meter -f -o %s " % out_file
    cmd += "'%s/%s/?" % (endpoint, method)
    cmd += ("%s" % '&'.join(arglist))
    cmd += "&token=%s&format=json'" % token
    if verbose:
        print('** get test of %s' % method)
        print(cmd)
    os.system(cmd)
    try:
        computed = open(out_file).read()
        return json.loads(computed)
    except:
        return None

if __name__ == '__main__':
    endpoint = 'https://' + settings.LASAIR_URL + '/api'
    token    = settings.API_TOKEN
    verbose = True

    L = lasair.lasair_client(token, endpoint=endpoint)

##### Query method
    selected    = 'diaObjectId, ra, decl, gPSFlux'
    tables      = 'objects'
    conditions  = 'gPSFlux > 20000'
    input = {'selected': selected, 'tables': tables, 'conditions': conditions}

    r = gettest(input, 'query', verbose)
    if verbose: print('Query get returned %s' % lenornothing(r))

    r = curltest(input, 'query', verbose)
    if verbose: print('Query curl returned %s' % lenornothing(r))

    r = L.query(selected, tables, conditions, limit=10)
    if verbose: print('Query python returned %s' % lenornothing(r))

    if len(r) == 0:
        print('No objects found. Exiting test')
        sys.exit()

    objid = r[0]['diaObjectId']
    objra = r[0]['ra']
    objde = r[0]['decl']

##### Conesearch method
    radius = 20 # arc seconds
    input = {'ra': objra, 'dec': objde, 'radius': radius, 'requestType': 'all'}
    r = gettest(input, 'cone', verbose)
    if verbose: print('Cone get returned %s' % lenornothing(r))

    r = curltest(input, 'cone', verbose)
    if verbose: print('Cone curl returned %s' % lenornothing(r))

    r = L.cone(objra, objde, radius, requestType='nearest')
    if verbose: print('Cone python returned %s' % lenornothing(r))

##### Lightcurve method
    input = {'objectIds': objid}  # comma separated list
    r = gettest(input, 'lightcurves', verbose)
    if verbose: print('Lightcurves get returned %s' % lenornothing(r))

    r = curltest(input, 'lightcurves', verbose)
    if verbose: print('Lightcurve curl returned %s' % lenornothing(r))

    r = L.lightcurves([objid])  # python list
    if verbose: print('Lightcurve python returned %s' % lenornothing(r))

##### Sherlock/position method
    input = {'ra': objra, 'dec': objde, 'lite':True}
    r = gettest(input, 'sherlock/position', verbose)
    if verbose: print('sherlock/position get returned %s' % lenornothing(r))

    r = curltest(input, 'sherlock/position', verbose)
    if verbose: print('sherlock/position curl returned %s' % lenornothing(r))

    r = L.sherlock_position(objra, objde, lite=True)
    if verbose: print('sherlock/position python returned %s' % lenornothing(r))

##### Sherlock/object method
    input = {'objectId': objid}
    r = gettest(input, 'sherlock/object', verbose)
    if verbose: print('sherlock/object get returned %s' % lenornothing(r))
    
    r = curltest(input, 'sherlock/object', verbose)
    if verbose: print('sherlock/object curl returned %s' % lenornothing(r))

    r = L.sherlock_object([objid])
    if verbose: print('sherlock/object python returned %s' % lenornothing(r))
