# Fitting Bazin curves with pre-peak samples: Time-Wavelength
# In this notebook we conside the Bazin supernova light curve:
# 
# Define
# $$ f(\tau) = exp(-k_f \tau) / [1 + exp(-k_r \tau)] $$
# 
# so that $k_r$ is the rise-rate, and $k_f$ is the fall rate.
# 
# Define the black body spectrum as a function of wavelength and temperature as
# $$ B(\lambda, T) = 5000 / (\lambda^5 T^4 [(exp(Q/\lambda T) - 1]) $$
#                                           
# where Q = hc/k = 14.387 $\mu$m kK, meaning wavelength in microns and temperature in kilo-Kelvins.
# 
# We define the flux at time $t$ and wavelength $\lambda$ as
# $$ F(t) = A B(\lambda, T) f(t-t_0) $$
#                                           
# so that the 5 parameters of the fit are $A$, $T$, $t_0$, $k_f$, and $k_r$.
# 
# At early times, $\tau$ is large and negative and the Bazin function $f(\tau)$ can be approximated as
# $$ g(\tau) = exp(k \tau) $$
# where $k$ = $k_r - k_f$. Therefore the 4 parameters of the fit are $A$, $T$, $t_0$, $k$.
# 
# At these early times, before the peak, there is no knowledge of the fall rate of the curve, 
# so we do not expect a clear values for $k_f$.
# 
# In the following we make functions for the Bazin curve, its Exponential approximation, and the derivatives w.r.t. the parameters.

import math
import numpy as np

# Wavelengths of the ugrizy filters
wl = {
'u': 0.380,
'g': 0.500,
'r': 0.620,
'i': 0.740,
'z': 0.880,
'y': 1.000,
}

# ## Black body flux
def blackbody(wl, T):
    hck = 14.387
    return 5000*np.power(wl, -5.0)*np.power(T, -4.0) / (np.exp(hck/(wl*T)) - 1)

# ## Bazin Fit
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

# ## Exponential Fit
def expit(t, lam, p):
    A = p[0]
    T = p[1]
    k = p[2]
    er = np.exp(k*t)
    # scale the wavelength so the numbers are not so big/small
    f = A * blackbody(lam, T) * er
    return f

# # Pre peak and post peak
# The parameter $k_r$ controls the pre-peak rate of increase of flux, 
# and $k_f$ controls post-peak rate of decrease of flux.
# In the following, we vary $k_f$ to show this behaviour.

# Some intermediate functions for scipy.optimize.leastsq
def func_bazin(params, tlam, f):
    t,lam = tlam
    residual = f - bazin(t, lam, params)
    return residual

def func_expit(params, tlam, f):
    t,lam = tlam
    residual = f - expit(t, lam, params)
    return residual

# Convert the alert to three arrays
# Now we use the `scipy.optimize.leastsq` method to fit the sampled points,
from scipy.optimize import leastsq

def fit_bazin(alert, pbazin0, sigma):       
    sources = alert['diaForcedSourcesList'] + alert['diaSourcesList']
    sources = sorted(sources, key=lambda source: source['midPointTai'])
    tobs = [s['midPointTai']    for s in sources]
    avgtobs = sum(tobs)/len(tobs)
    tobs = [t-avgtobs for t in tobs]
    lobs = [wl[s['filterName']] for s in sources]
    fobs = [s['psFlux']         for s in sources]
    maxfobs = max(fobs)
    fobs = [f/maxfobs for f in fobs]

    npoint = len(tobs)
    tlobs = np.vstack((tobs, lobs))
    SST = np.sum((fobs - np.mean(fobs))**2)

    (fit, cov, infodict, errmsg, ier) = \
        leastsq(func_bazin, pbazin0, (tlobs, fobs), full_output=1)
    try:
        err = np.sqrt(np.diag(cov))*sigma
    except:
        err = [0,0,0,0,0]

    SSE = np.sum(func_bazin(fit, tlobs, fobs)**2)
#    AIC_bazin = 100 + npoint*math.log(SSE_bazin/npoint) + 2*5
    Rsq = SSE/SST
    if Rsq > 0.25: return (1.0, None)
    dict = {}
    dict['bazinExpTemp'] = fit[1]
    dict['bazinExpRiseRate'] = fit[3]
    dict['bazinExpFallRate'] = fit[4]
    if dict['bazinExpRiseRate'] < 0.0: return (1.0, None)
    if dict['bazinExpFallRate'] < 0.0: return (1.0, None)
    if dict['bazinExpRiseRate'] > 2.0: return (1.0, None)
    if dict['bazinExpFallRate'] > 2.0: return (1.0, None)
    
    dict['bazinExpTempErr'] = err[1]
    dict['bazinExpRiseRateErr'] = err[3]
    dict['bazinExpFallRateErr'] = err[4]
    if dict['bazinExpFallRateErr'] > dict['bazinExpFallRate']: return (1.0, None)
    if dict['bazinExpRiseRateErr'] > dict['bazinExpRiseRate']: return (1.0, None)
    return (Rsq, dict)

def fit_expit(alert, pexpit0, sigma):           
    sources = alert['diaForcedSourcesList'] + alert['diaSourcesList']
    sources = sorted(sources, key=lambda source: source['midPointTai'])
    tobs = [s['midPointTai']    for s in sources]
    avgtobs = sum(tobs)/len(tobs)
    tobs = [t-avgtobs for t in tobs]
    lobs = [wl[s['filterName']] for s in sources]
    fobs = [s['psFlux']         for s in sources]
    maxfobs = max(fobs)
    fobs = [f/maxfobs for f in fobs]

    npoint = len(tobs)
    tlobs = np.vstack((tobs, lobs))
    SST = np.sum((fobs - np.mean(fobs))**2)

    (fit, cov, infodict, errmsg, ier) = \
        leastsq(func_expit, pexpit0, (tlobs, fobs), full_output=1)
    try:
        err = np.sqrt(np.diag(cov))*sigma
    except:
        return (1.0, None)
    
    SSE = np.sum(func_expit(fit, tlobs, fobs)**2)
    Rsq = SSE/SST
    if Rsq > 0.25: return (1.0, None)

    dict = {}
    dict['bazinExpTemp'] = fit[1]
    dict['bazinExpRiseRate'] = fit[2]
    if dict['bazinExpRiseRate'] < 0.0: return None
    if dict['bazinExpRiseRate'] > 2.0: return None
    
    dict['bazinExpTempErr'] = err[1]
    dict['bazinExpRiseRateErr'] = err[2]
    if dict['bazinExpRiseRateErr'] > dict['bazinExpRiseRate']: return None
    return (Rsq, dict)

def fitBazinExpBB(alert, pexpit0, pbazin0, sigma):
    if len(alert['diaSourcesList']) < 4:
        return None
    (Rsqe, dicte) = fit_expit(alert, pexpit0, sigma)
    (Rsqb, dictb) = fit_bazin(alert, pbazin0, sigma)
    if dicte and dictb:
        if Rsqe < Rsqb: return dicte
        else:           return dictb
    elif dicte:
        return dicte
    elif dictb:
        return dictb
    else:
        return None

##################################################
from features.FeatureGroup import FeatureGroup

class bazinExpBlackBody(FeatureGroup):
    """Min and Max time of the diaSources"""

    _features = [
        "bazinExpRiseRate", 
        "bazinExpFallRate", 
        "bazinExpTemp",
        "bazinExpRiseRateErr", 
        "bazinExpFallRateErr", 
        "bazinExpTempErr",
    ]    

    def run(self):
        A = 1
        T = 4
        t0 = 0
        kr = 0.01
        kf = 0.005
        pexpit0 = [A, T, kr-kf]
        pbazin0 = [A, T, t0, kr, kf]
        sigma = 0.1

        dict = fitBazinExpBB(self.alert, pexpit0, pbazin0, sigma)
        return dict
