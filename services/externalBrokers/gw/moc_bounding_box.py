import os, sys
import math
import healpy
import warnings
import random
from mocpy import MOC
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord
sys.path.append('../../../common')
import settings

def makelist(n):
    ralist = []
    delist = []
    for i in range(n):
        ra = random.randrange(0, 360000000) / 1000000
        de = round(math.asin(random.uniform(-1, 1)) * 180/math.pi, 6)
        ralist.append(ra)
        delist.append(de)
    return {"ralist":ralist, "delist":delist}

def moc_bounding_box(moc):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pixlist = moc.get_boundaries()

    maxra = 0
    minra = 360
    maxde = -90
    minde = 90
    for pix in pixlist:
        for p in pix:
            if p.ra.degree  > maxra: maxra = p.ra.degree
            if p.ra.degree  < minra: minra = p.ra.degree
            if p.dec.degree > maxde: maxde = p.dec.degree
            if p.dec.degree < minde: minde = p.dec.degree
    if maxra-minra > 300: 
        None  # wrapping around, can't do this
    else:
        return {'minra':minra, 'maxra':maxra, 'minde':minde, 'maxde':maxde}

def moc2sql(mocfilename):
    """ Return the SQL cluase that implements the bounding box.
    If the MOC covers the line of RA=0, we just can't do it.
    """
    moc = MOC.from_fits(settings.GW_DIRECTORY +'/'+ mocfilename +'/90.moc')
    r = moc_bounding_box(moc)
    if r is None:
        return ''
    else:
        fmt = 'AND ra BETWEEN %.4f AND %.4f AND decl BETWEEN %.4f AND %.4f'
        return fmt % (r['minra'], r['maxra'], r['minde'], r['maxde'])

def count(moc, ralist, delist):
    """ Count the number in the MOC
    """
    result = moc.contains_lonlat(ralist * u.deg, delist * u.deg)
    n_in_moc = 0
    for i in range(len(ralist)):
        if result[i]: n_in_moc += 1
    return n_in_moc

def checkit(mocfilename, points):
    """ Count how many points in the MOC, then apply the bounding box and count again. 
    Should get the same numbers
    """
    ralist = points['ralist']
    delist = points['delist']
    moc = MOC.from_fits(settings.GW_DIRECTORY +'/'+ mocfilename +'/90.moc')
    n1 = count(moc, ralist, delist)

    r = moc_bounding_box(moc)
    if not r:
        print('WRAP %s' % mocfilename)
        return
    ralist2 = []
    delist2 = []
    for ra,de in zip(ralist, delist):
        if ra>r['minra'] and ra<r['maxra'] and de>r['minde'] and de<r['maxde']:
            ralist2.append(ra)
            delist2.append(de)
    n2 = count(moc, ralist2, delist2)

    print('plain: %d of %d, bbox: %d of %d, for %s' % (n1, len(ralist), n2, len(ralist2), mocfilename))
    assert(n1 == n2)

if __name__ == "__main__":
    """ Intended to run in a cron to harvest GW alerts that appear in the directory
    """
    checking = False
    if checking:
        points = makelist(1000)

    for file in sorted(os.listdir(settings.GW_DIRECTORY)):
        if file.startswith('S') or file.startswith('M'):
            otherId = file
            for version in os.listdir(settings.GW_DIRECTORY+'/'+otherId):
                if version.startswith('20'):
                    mocfilename = '%s/%s' % (otherId, version)
                    if checking:
                        checkit(mocfilename, points)
                    else:
                        sql = moc2sql(mocfilename)
                        print(mocfilename, sql)
