import os, sys, json, io, yaml, base64, traceback
from mocpy import MOC, WCS
import astropy.units as u
import matplotlib.pyplot as plt
from yaml import CLoader as Loader, CDumper as Dumper
from datetime import datetime, timedelta
sys.path.append('../../../common')
from src import db_connect

def mjd2date(mjd):
    date = datetime.strptime("1858/11/17", "%Y/%m/%d")
    date += timedelta(mjd)
    return date

def bytes2string(bytes):
    base64_bytes   = base64.b64encode(bytes)
    str = base64_bytes.decode('utf-8')
    return str

def string2bytes(str):
    base64_bytes  = str.encode('utf-8')
    bytes = base64.decodebytes(base64_bytes)
    return bytes

def read_moc(datadir, name):
    f = open(datadir + '/%s.moc' % name, 'rb')
    bytes = f.read()
    f.close()
    return bytes

def make_moc(mocbytes):
    inbuf = io.BytesIO(mocbytes)
    moc = MOC.from_fits(inbuf)
    return moc

def make_image(moc10, moc50, moc90):
    moc10 = make_moc(moc10)
    moc50 = make_moc(moc50)
    moc90 = make_moc(moc90)
    notmoc = moc10.complement()
    fig = plt.figure(111, figsize=(8, 5))
    with WCS(fig, fov=360 * u.deg, projection="AIT") as wcs:
        ax = fig.add_subplot(1, 1, 1, projection=wcs)
        notmoc.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="lightgray", linewidth=None)
        moc90.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="red",   linewidth=None)
        moc50.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="orange", linewidth=None)
        moc10.fill(ax=ax, wcs=wcs, alpha=1.0, fill=True, color="cyan",  linewidth=None)

    plt.grid(color="black", linestyle="dotted")
    outbuf = io.BytesIO()
    plt.savefig(outbuf, format='png', bbox_inches='tight', pad_inches=-0.85, dpi=200)
    bytes = outbuf.getvalue()
    outbuf.close()
    return bytes

def getDone(dir, eventId, version):
    flag = '%s/%s/%s/done' % (dir, eventId, version)
    return os.path.isfile(flag)

def setDone(dir, eventId, version):
    flag = '%s/%s/%s/done' % (dir, eventId, version)
    datadir = '%s/%s/%s' % (dir, eventId, version)
    os.system('touch ' + flag) 

def handleMmaWatchmap(database, dir, eventId, version):
    datadir = '%s/%s/%s' % (dir, eventId, version)
    f = open(datadir + '/meta.yaml')
    data = yaml.load(f, Loader=Loader)
    f.close()

    params = {
        'classification': data['ALERT']['event']['classification'],
        'far': data['ALERT']['event']['far'],
    }
 #   radec = data['EXTRA']['central coordinate']['equatorial'].split()
    radec = '0.0 0.0'.split()
    loc = {
        'RA'      :float(radec[0].strip()), 
        'Dec'     :float(radec[1].strip()), 
        'distmean':data['HEADER']['DISTMEAN'], 
        'diststd' :data['HEADER']['DISTSTD'],
        }
    params['location'] = loc

    event_tai  = data['HEADER']['MJD-OBS']
    event_date = mjd2date(event_tai)

    date_active = event_date   #### HACK
    area10 = data['EXTRA']['area10']
    area50 = data['EXTRA']['area50']
    area90 = data['EXTRA']['area90']

    # decide if we want it
    if area90 > 500:
        return '90% area > 500'
    if loc['distmean'] > 200:
        return 'distance > 200 Mpc'

    jparams = json.dumps(params)

    moc10 = read_moc(datadir, '10')
    moc50 = read_moc(datadir, '50')
    moc90 = read_moc(datadir, '90')
    mocimage = make_image(moc10, moc50, moc90)

    b64moc10 = bytes2string(moc10)
    b64moc50 = bytes2string(moc50)
    b64moc90 = bytes2string(moc90)
    b64mocimage = bytes2string(mocimage)

    active = 1
    public = 1

    namespace = 'LVK'
    otherId   = eventId
    fits      = ''
    more_info = ''

    query = """
    INSERT INTO mma_areas (
        event_tai, event_date, mocimage, 
        namespace, otherId, version, more_info,
        area10, area50, area90, params
    ) VALUES (
        %f, "%s", "%s",
        "%s", "%s", "%s","%s",
        %f, %f, %f, '%s'
    ) """

    query = query % ( \
        event_tai, event_date, b64mocimage,  \
        namespace, otherId, version, more_info, \
        area10, area50, area90, jparams \
    )

    cursor = database.cursor(buffered=True, dictionary=True)
    cursor.execute (query)
    database.commit()
    return ''

def handle_event(database, dir, eventId):
    ningested = 0
    for version in os.listdir(dir+'/'+eventId):
        if version.startswith('20'):
            if not getDone(dir, eventId, version):
                try:
                    message = handleMmaWatchmap(database, dir, eventId, version)
                    if len(message) == 0:
                        ningested += 1
                        print(eventId, version, 'ingested')
                    else:
                        print(eventId, version, 'not ingested', message)
                    setDone(dir, eventId, version)
                except Exception as e:
                    print(traceback.format_exc())
    return ningested

############
import sys
dir = '/mnt/cephfs/lasair/mma/gw/'
database = db_connect.remote()

ningested = 0
if len(sys.argv) > 1:
    eventId = sys.argv[1]
    handle_event(dir, eventId)
else:
    for file in sorted(os.listdir(dir)):
        if file.startswith('S') or file.startswith('M'):
            eventId = file
            ningested += handle_event(database, dir, eventId)
print(ningested, 'event versions ingested')
