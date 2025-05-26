import math
import numpy as np
import matplotlib.pyplot as plt

WL    = [0.380,     0.500,     0.620,     0.740,     0.880,     1.000, ]
BANDS = ['u',       'g',       'r'  ,     'i'  ,     'z'  ,     'y'    ]
color = ["#9900cc", "#3366ff", "#33cc33", "#ffcc00", "#ff0000", "#cc6600"]
nwl   = len(BANDS)
sigma = 10
maxfev= 500

def blackbody(wl, T):
    hck = 14.387
    return np.power(wl, -3.0) / (np.exp(hck/(wl*T)) - 1)

def g_minus_r(T):
    gband = 1
    rband = 2
    flux_ratio = blackbody(WL[gband], T) / \
                 blackbody(WL[rband], T)
    return -2.5 * math.log10(flux_ratio)

def bazin(t, lam, p):
    A = p[0]
    T = p[1]
    t0 = p[2]
    kr = p[3]
    kf = p[4]
    tau = t - t0
    ef = np.exp(-kf*tau)
    er = np.exp(-kr*tau)
    # scale the wavelength so the numbers are not so big/small
    f = A * blackbody(lam, T) * ef/(1+er)
    return f

def expit(t, lam, p):
    A = p[0]
    T = p[1]
    k = p[2]
    er = np.exp(k*t)
    # scale the wavelength so the numbers are not so big/small
    f = A * blackbody(lam, T) * er
    return f

def func_bazin(params, tlam, f):
    t,lam = tlam
    residual = f - bazin(t, lam, params)
    return residual

def func_expit(params, tlam, f):
    t,lam = tlam
    residual = f - expit(t, lam, params)
    return residual

from scipy.optimize import leastsq
def fit_bazin(tobs, lobs, fobs, pbazin0, verbose=False):       
    npoint = len(tobs)
    tlobs = np.vstack((tobs, lobs))
    SST = np.sum((fobs - np.mean(fobs))**2)

    (fit, cov, infodict, errmsg, ier) = \
        leastsq(func_bazin, pbazin0, (tlobs, fobs), full_output=1, maxfev=maxfev)

    nfev = infodict['nfev']
    if nfev >= maxfev:
        return None

    try:
        err = np.sqrt(np.diag(cov))*sigma
    except:
        err = [0,0,0,0,0]

    SSE = np.sum(func_bazin(fit, tlobs, fobs)**2)

# https://en.wikipedia.org/wiki/Akaike_information_criterion
# with 5 degrees of freedom
    AIC = 100 + npoint*math.log(SSE/npoint) + 2*5

    Rsq = SSE/SST
    if Rsq > 0.25: return None
    dict = {'npoint':npoint, 'Rsq':Rsq, 'AIC':AIC, 'nfev':nfev}
    dict['A'] = fit[0]
    dict['T'] = fit[1]
    dict['t0'] = fit[2]
    dict['kr'] = fit[3]
    dict['kf'] = fit[4]
    if dict['kr'] < 0.0: 
        if verbose: print('kr<0')
        return None
    if dict['kf'] < 0.0: 
        if verbose: print('kf<0')
        return None
    if dict['kr'] > 15.0: 
        if verbose: print('kr>15')
        return None
    if dict['kf'] > 2.0: 
        if verbose: print('kf>2')
        return None
    
#    dict['Aerr'] = err[0]
#    dict['Terr'] = err[1]
#    dict['t0err'] = err[2]
#    dict['krerr'] = err[3]
#    dict['kferr'] = err[4]
#    if dict['kferr'] > dict['kf']: 
#        print('kferr>kf')
#        return None
#    if dict['krerr'] > dict['kr']: 
#        print('krerr>kr')
#        return None

    maxq = 0
    maxwl = 0
    for wl in WL:
        q = blackbody(wl, dict['T'])
        if q > maxq: 
            maxq = q
            maxwl = wl

    tau = -math.log(dict['kf']/(dict['kr']-dict['kf'])) / dict['kr']
    dict['peakTime'] = dict['t0'] + tau
    dict['peakValue'] = bazin(dict['peakTime'], maxwl, fit)
    
    return dict

def fit_expit(tobs, lobs, fobs, pexpit0, verbose=True):           
    npoint = len(tobs)
    tlobs = np.vstack((tobs, lobs))
    SST = np.sum((fobs - np.mean(fobs))**2)

    (fit, cov, infodict, errmsg, ier) = \
        leastsq(func_expit, pexpit0, (tlobs, fobs), full_output=1, maxfev=maxfev)

    nfev = infodict['nfev']
    if nfev >= maxfev:
        return None
   
    try:
        err = np.sqrt(np.diag(cov))*sigma
    except:
        return None
    
    SSE = np.sum(func_expit(fit, tlobs, fobs)**2)

# https://en.wikipedia.org/wiki/Akaike_information_criterion
# with 3 degrees of freedom
    AIC = 100 + npoint*math.log(SSE/npoint) + 2*3

    Rsq = SSE/SST
    if Rsq > 0.35: 
        return None
    dict = {'npoint':npoint, 'Rsq':Rsq, 'AIC':AIC, 'nfev':nfev}

    dict['A'] = fit[0]
    dict['T'] = fit[1]
    dict['k'] = fit[2]
    if dict['k'] < 0.0: return None
    if dict['k'] > 2.0: return None
    
    dict['Aerr'] = err[0]
    dict['Terr'] = err[1]
    dict['kerr'] = err[2]
    if dict['kerr'] > dict['k']: return None
    
    return dict
