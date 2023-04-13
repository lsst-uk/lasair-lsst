from django.db import connection
import settings
import math


def conesearch_impl(cone):
    """*perform a conesearch query*

    **Key Arguments:**

    - `cone` -- the search string

    **Usage:**

    ```python
    from lasair.apps.search import conesearch_impl
    data = conesearch_impl(cone)
    ```           
    """
    ra = dec = radius = 0.0
#    hitdict = {}
    hitlist = []
    d = readcone(cone)

    if 'objectIds' in d:
        data = {'cone': cone, 'hitlist': d['objectIds'],
                'message': 'Found ZTF object names'}
        return data

    if 'TNSname' in d:
        cursor = connection.cursor()
        query = 'SELECT objectId FROM watchlist_hits WHERE wl_id=%d AND name="%s"'
        query = query % (settings.TNS_WATCHLIST_ID, d['TNSname'])
        cursor.execute(query)
        hits = cursor.fetchall()
        message = '%s not found in TNS' % cone
        for hit in hits:
            hitlist.append(hit[0])
            message = '%s found in TNS' % cone
        data = {'TNSname': d['TNSname'], 'hitlist': hitlist, 'message': message}
        return data

    if 'ra' in d:
        ra = d['ra']
        dec = d['dec']
        radius = d['radius']
        dra = radius / (3600 * math.cos(dec * math.pi / 180))
        dde = radius / 3600
        cursor = connection.cursor()
        query = 'SELECT objectId,ramean,decmean FROM objects WHERE ramean BETWEEN %f and %f AND decmean BETWEEN %f and %f' % (ra - dra, ra + dra, dec - dde, dec + dde)
#        query = 'SELECT DISTINCT objectId FROM candidates WHERE ra BETWEEN %f and %f AND decl BETWEEN %f and %f' % (ra-dra, ra+dra, dec-dde, dec+dde)
        cursor.execute(query)
        hits = cursor.fetchall()
        for hit in hits:
            #            dist = distance(ra, dec, hit[1], hit[2]) * 3600.0
            #            if dist < radius:
            #                hitdict[hit[0]] = (hit[1], hit[2], dist)
            hitlist.append(hit[0])
        message = d['message'] + '<br/>%d objects found in cone' % len(hitlist)
        data = {'ra': ra, 'dec': dec, 'radius': radius, 'cone': cone,
                'hitlist': hitlist, 'message': message}
        return data
    else:
        data = {'cone': cone, 'message': d['message']}
        return data


def readcone(cone):
    """*parse conesearch request*

    **Key Arguments:**

    - `cone` -- the search string

    **Usage:**

    ```python
    from lasair.apps.search import readcone
    parsedSearch = readcone(cone)
    ```           
    """
    error = False
    message = ''
    cone = cone.replace(',', ' ').replace('\t', ' ').replace(';', ' ').replace('|', ' ')
    tok = cone.strip().split()
#    message += str(tok)

# if tokens begin with 'SN' or 'AT', must be TNS identifier
    TNSname = None
    if len(tok) == 1:
        t = tok[0]
        if t[0:2] == 'SN' or t[0:2] == 'AT':
            return {'TNSprefix': t[0:2], 'TNSname': t[2:]}
        if t[0:2] == '20':
            return {'TNSprefix': '', 'TNSname': t}
        if t[0:3] == 'ZTF':
            return {'objectIds': tok}

# if odd number of tokens, must end with radius in arcsec
    radius = 5.0
    if len(tok) % 2 == 1:
        try:
            radius = float(tok[-1])
        except:
            error = True
        tok = tok[:-1]

# remaining options tok=2 and tok=6
#   radegrees decdegrees
#   h:m:s   d:m:s
#   h m s   d m s
    if len(tok) == 2:
        try:
            ra = float(tok[0])
            de = float(tok[1])
        except:
            try:
                ra = sexra(tok[0].split(':'))
                de = sexde(tok[1].split(':'))
            except:
                error = True

    if len(tok) == 6:
        try:
            ra = sexra(tok[0:3])
            de = sexde(tok[3:6])
        except:
            error = True

    if error:
        return {'message': 'cannot parse ' + cone + ' ' + message}
    else:
        message += 'RA,Dec,radius=%.5f,%.5f,%.1f' % (ra, de, radius)
        return {'ra': ra, 'dec': de, 'radius': radius, 'message': message}


def sexra(tok):
    """*convert sexigesimal RA to degrees*

    **Key Arguments:**

    - `tok` -- the RA to convert

    **Usage:**

    ```python
    from lasair.apps.search import sexra
    raDeg = sexra(raSex)
    ```           
    """
    return 15 * (float(tok[0]) + (float(tok[1]) + float(tok[2]) / 60) / 60)


def sexde(tok):
    """*convert sexigesimal Dec to degrees*

    **Key Arguments:**

    - `tok` -- the Dec to convert

    **Usage:**

    ```python
    from lasair.apps.search import decra
    decDeg = sexdec(decSex)
    ```           
    """
    if tok[0].startswith('-'):
        de = (float(tok[0]) - (float(tok[1]) + float(tok[2]) / 60) / 60)
    else:
        de = (float(tok[0]) + (float(tok[1]) + float(tok[2]) / 60) / 60)
    return de
