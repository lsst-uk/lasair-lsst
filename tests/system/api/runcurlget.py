import json
import os
import sys
sys.path.append('../../../common')

try:
    import settings
    token = settings.token
except:
    token = '4b762569bb349bd8d60f1bc7da3f39dbfaefff9a'

try:
    url = f"https://{settings.LASAIR_URL}/api"
except:
    url = 'https://lasair-lsst.lsst.ac.uk/api'

out_file = 'tmp.json'


def curlgettest(input, method, case):
    curltest(input, method, case)
    gettest(input, method, case)


def curltest(input, method, case):
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
    cmd += "%s/%s/" % (url, method)
    print('** curl test of %s:%s' % (method, case))
    print(cmd)
    os.system(cmd)
    try:
        computed = open(out_file).read()
        json.loads(computed)
        print('---> test succeeded\n\n')
    except:
        print('---> test failed\n\n')


def gettest(input, method, case):
    try:
        os.remove(out_file)
    except FileNotFoundError:
        pass
    arglist = []
    for k, v in input.items():
        arglist.append('%s=%s' % (k, v))
    cmd = "curl --no-progress-meter -f -o %s " % out_file
    cmd += "'%s/%s/?" % (url, method)
    cmd += "%s" % '&'.join(arglist)
    cmd += "&token=%s&format=json'" % token
    print('** get test of %s:%s' % (method, case))
    print(cmd)
    os.system(cmd)
    try:
        computed = open(out_file).read()
        json.loads(computed)
        print('---> test succeeded\n\n')
    except:
        print('---> test failed\n\n')


input = {'ra': 194.494, 'dec': 48.851, 'radius': 240.0, 'requestType': 'all'}
curlgettest(input, 'cone', '')

input = {'objectIds': 'ZTF20acpwljl,ZTF20acqqbkl,ZTF20acplggt'}
curlgettest(input, 'lightcurves', '')

input = {'selected': 'objectId,gmag', 'tables': 'objects', 'conditions': 'gmag<12.0'}
curlgettest(input, 'query', '')

input = {'objectIds': 'ZTF20acpwljl,ZTF20acqqbkl,ZTF20acplggt'}
curlgettest(input, 'sherlock/objects', '')

input = {'ra': 124.879948, 'dec': -6.020519, 'lite': True}
curlgettest(input, 'sherlock/position', '')

input = {'regex': '.*SN.*'}
curlgettest(input, 'streams', 'regex')

input = {'limit': 3}
curlgettest(input, 'streams/2SN-likecandidates', '')
