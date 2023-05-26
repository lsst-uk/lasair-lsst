import math
import numpy as np
from scipy.optimize import leastsq

# ugrizy filter names
filterNames = ['u', 'g', 'r', 'i', 'z', 'y']

def expit(t, p):
    A = p[0]
    k = p[1]
    er = np.exp(k*t)
    # scale the wavelength so the numbers are not so big/small
    return A * er

def func_expit(params, t, f):
    residual = f - expit(t, params)
    return residual

def fitExp(alert, pexpit0, sigma):           
    sources = alert['diaForcedSourcesList'] + alert['diaSourcesList']
    sources = sorted(sources, key=lambda source: source['midPointTai'])

    all_tobs = [s['midPointTai']    for s in sources]
    if len(all_tobs) < 1:
        return None
    avgtobs = sum(all_tobs)/len(all_tobs)

    all_fobs = [s['psFlux']         for s in sources]
    maxfobs = max(all_fobs)

    dict = {}
    for filterName in filterNames:
        tobs = []
        fobs = []
        for s in sources:
            if s['filterName'] == filterName:
                tobs.append(s['midPointTai'] - avgtobs)
                fobs.append(s['psFlux'] / maxfobs)

        npoint = len(tobs)
        dict[filterName + '_n'] = npoint
        dict[filterName + '_Rsq'] = 1.0
        dict[filterName + '_k'] = None
        dict[filterName + '_kerr'] = None
        if npoint < 2:
            continue
        tobs = np.array(tobs)
        fobs = np.array(fobs)
        SST = np.sum((fobs - np.mean(fobs))**2)

        (fit, cov, infodict, errmsg, ier) = \
             leastsq(func_expit, pexpit0, (tobs, fobs), full_output=1)
        try:
            err = np.sqrt(np.diag(cov))*sigma
        except:
            print('negative cov matrix')
            continue
    
        SSE = np.sum(func_expit(fit, tobs, fobs)**2)
#    AIC_bazin = 100 + npoint*math.log(SSE_bazin/npoint) + 2*5
        Rsq = SSE/SST
        if Rsq > 0.25: continue
        dict[filterName + '_n'] = len(tobs)
        dict[filterName + '_Rsq'] = Rsq
        dict[filterName + '_k'] = fit[1]
        dict[filterName + '_kerr'] = err[1]

    return dict

if __name__ == '__main__':
    import os, sys, json
    A = 1
    k = 0.1
    pexpit0 = [A, k]

    sigma = 0.1

    if len(sys.argv) > 1:
        samples = sys.argv[1]
    else:
        print('Must add name of sample set')
        sys.exit()
    for file in sorted(os.listdir(samples)):
        if not file.endswith('.json'):
            continue
        try:
            alert = json.loads(open(samples+'/'+file).read())
        except Exception as e:
            print(file, e)
            continue

        dict = fitExp(alert, pexpit0, sigma)
        print(file)
        print(dict)
        print()
