"""
Run Lasair API test suite using both GET and POST.

Usage:
    runcurlget.py [--url=URL]
                  [--token=TOKEN]

Options:
    --url=URL     URL of the Lasair API, e.g. https://lasair-lsst.lsst.ac.uk/api
    --token=TOKEN API token to use
"""

from docopt import docopt
import json
import os
import sys
sys.path.append('../../../common')

try:
    import settings
except:
    pass


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


if __name__ == '__main__':
    args = docopt(__doc__)
    if args.get('--url'):
        url = args.get('--url')
    else:
        try:
            url = f"https://{settings.LASAIR_URL}/api"
        except:
            url = 'https://lasair-lsst.lsst.ac.uk/api'
    if args.get('--token'):
        token = args.get('--token')
    else:
        try:
            token = f"{settings.API_TOKEN}"
        except:
            token = '4b762569bb349bd8d60f1bc7da3f39dbfaefff9a'

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
