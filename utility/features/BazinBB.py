import os, sys, json, random, math

wl = { 'u': 0.380, 'g': 0.500, 'r': 0.620, 'i': 0.740, 'z': 0.880, 'y': 1.000, }

def blackbody(wl, T):
    hck = 14.387
    return 5000*math.pow(wl, -5.0)*math.pow(T, -4.0) / (math.exp(hck/(wl*T)) - 1)

def bazinBB(t, lam, p):
    A = p[0]
    T = p[1]
    t0 = p[2]
    kr = p[3]
    kf = p[4]
    tau = t - t0
    ef = math.exp(-kf*tau)
    er = math.exp(-kr*tau)
    # scale the wavelength so the numbers are not so big/small
    f = A * blackbody(lam, T) * ef/(1+er)
    return f

def makeObject(diaObjectId):
    tmin = -20
    tmax =  8
    nsource = 40
    sigma = 1000
    p = [100000, 5, 0, 0.3, 0.1]
    t = []
    for i in range(nsource):
        t.append(tmin + random.random()*(tmax-tmin))
    t = sorted(t)

    idet = -1
    fluxList = []
    filterNameList = []
    for i in range(nsource):
        filterName = random.choice(list(wl.keys()))
        flux = bazinBB(t[i], wl[filterName], p) + sigma*random.normalvariate(0.0, 1.0)
        filterNameList.append(filterName)
        fluxList.append(flux)
        if idet == -1 and flux > 5*sigma:
            idet = i
            inondet = idet - random.randint(1,4)
    if inondet <= 0:
        return None

    print(diaObjectId, inondet, idet, nsource)

    diaSourcesList = []
    diaForcedSourcesList = []
    diaNondetectionLimitsList = []
    for i in range(0, nsource):
        diaSourceId = 1000+i
        if i < inondet:
            diaNondetectionLimitsList.append({
                "midPointTai": t[i],
                "filterName": filterNameList[i],
                "diaNoise": fluxList[i],
            })
        elif i < idet:
            diaForcedSourcesList.append({
                "diaSourceId": random.randint(1000, 5000),
                "midPointTai": t[i],
                "filterName": filterNameList[i],
                "psFlux": fluxList[i],
                "psFluxErr": sigma,
            })
        else:
            diaSourcesList.append({
                "diaSourceId": random.randint(1000, 5000),
                "midPointTai": t[i],
                "filterName": filterNameList[i],
                "psFlux": fluxList[i],
                "psFluxErr": sigma,
            })
    diaSourcesList            = sorted(diaSourcesList,            key=lambda ds:ds['midPointTai'])
    diaForcedSourcesList      = sorted(diaForcedSourcesList,      key=lambda ds:ds['midPointTai'])
    diaNondetectionLimitsList = sorted(diaNondetectionLimitsList, key=lambda ds:ds['midPointTai'])

    diaObject = {
        'diaObjectId': diaObjectId,
        'ra': 0.0,
        'decl': 0.0,
        'radecTai': 0.0,
        'uPSFluxMean': 0.0,
        'gPSFluxMean': 0.0,
        'rPSFluxMean': 0.0,
        'iPSFluxMean': 0.0,
        'zPSFluxMean': 0.0,
        'yPSFluxMean': 0.0,
    }

    alert = {
        'diaObject'                : diaObject,
        'diaSourcesList'           : diaSourcesList,
        'diaForcedSourcesList'     : diaForcedSourcesList,
        'diaNondetectionLimitsList': diaNondetectionLimitsList,
    }
    return alert

#######################
to = 'BazinBB'
for i in range(10):
    j = makeObject(1000 + i)
    gfile = to + '/' + str(j['diaObject']['diaObjectId']) + '.json'
    f = open(gfile, 'w')
    f.write(json.dumps(j, indent=2))
    f.close()
