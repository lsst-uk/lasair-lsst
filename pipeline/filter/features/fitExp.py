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

def fitExpImpl(alert, pexpit0, sigma, verbose):
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
        dict[filterName + 'ExpRate']    = None
        dict[filterName + 'ExpRateErr'] = None
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
            if verbose:
                print('fitExp: Filter %s: negative cov matrix' % filterName)
            continue

        SSE = np.sum(func_expit(fit, tobs, fobs)**2)
#    AIC_bazin = 100 + npoint*math.log(SSE_bazin/npoint) + 2*5
        Rsq = SSE/SST
        if Rsq > 0.25: 
            if verbose:
                print('fitExp: Filter %s: Rsq less than 0.25' % filterName)
            continue
        dict[filterName + 'ExpRate']    = fit[1]
        dict[filterName + 'ExpRateErr'] = err[1]

    return dict

#############################################
from features.FeatureGroup import FeatureGroup
class fitExp(FeatureGroup):
    """Fit exponentials separately to each filter"""

    _features = [
        "uExpRate", "uExpRateErr",
        "gExpRate", "gExpRateErr",
        "rExpRate", "rExpRateErr",
        "iExpRate", "iExpRateErr",
        "zExpRate", "zExpRateErr",
        "yExpRate", "yExpRateErr",
    ]
    def run(self):
        A = 1
        k = 0.1
        pexpit0 = [A, k]
        sigma = 0.1
        return fitExpImpl(self.alert, pexpit0, sigma, self.verbose)
