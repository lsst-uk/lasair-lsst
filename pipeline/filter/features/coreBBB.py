import math
import numpy as np
import matplotlib.pyplot as plt

sigma=10

# Wavelengths of the ugrizy filters

wl = [
0.380,  # u not using this filter
0.500,  # g
0.620,  # r
0.740,  # i
0.880,  # z
1.000  # y
]
wltag = [
'u',  # u not using this filter
'g',
'r',
'i',
'z',
'y'
]
color = ["#9900cc", "#3366ff", "#33cc33", "#ffcc00", "#ff0000", "#cc6600"]
nwl = 6

def blackbody(wl, T):
    hck = 14.387
    return np.power(wl, -3.0) / (np.exp(hck/(wl*T)) - 1)

def g_minus_r(T):
    flux_ratio = blackbody(wl[1], T) / blackbody(wl[2], T)
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
def fit_bazin(tobs, lobs, fobs, pbazin0, verbose=True):       
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
    if Rsq > 0.25: return None
    dict = {'npoint':npoint, 'Rsq':Rsq}
    dict['A'] = fit[0]
    dict['T'] = fit[1]
    dict['t0'] = fit[2]
    dict['kr'] = fit[3]
    dict['kf'] = fit[4]
    if dict['kr'] < 0.0: 
        print('kr<0')
        return None
    if dict['kf'] < 0.0: 
        print('kf<0')
        return None
    if dict['kr'] > 15.0: 
        print('kr>15')
        return None
    if dict['kf'] > 2.0: 
        print('kf>2')
        return None
    
    dict['Aerr'] = err[0]
    dict['Terr'] = err[1]
    dict['t0err'] = err[2]
    dict['krerr'] = err[3]
    dict['kferr'] = err[4]
#    if dict['kferr'] > dict['kf']: 
#        print('kferr>kf')
#        return None
#    if dict['krerr'] > dict['kr']: 
#        print('krerr>kr')
#        return None
    
    return dict


def fit_expit(tobs, lobs, fobs, pexpit0, verbose=True):           
    npoint = len(tobs)
    tlobs = np.vstack((tobs, lobs))
    SST = np.sum((fobs - np.mean(fobs))**2)

    (fit, cov, infodict, errmsg, ier) = \
        leastsq(func_expit, pexpit0, (tlobs, fobs), full_output=1)
    try:
        err = np.sqrt(np.diag(cov))*sigma
    except:
        return None
    
    SSE = np.sum(func_expit(fit, tlobs, fobs)**2)
#    AIC_bazin = 100 + npoint*math.log(SSE_bazin/npoint) + 2*5
    Rsq = SSE/SST
    if Rsq > 0.25: return None
    dict = {'npoint':npoint, 'Rsq':Rsq}

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

def plot(lc, dict, filename, isbazin):
    npoint = len(lc['t'])
    tobs = lc['t']
    lobs = [wl[i] for i in lc['pb']]
    fobs = lc['flux']

    plt.rcParams.update({'font.size': 8})
    fig = plt.figure(figsize=(6,6))
    ax = plt.subplot(1, 1, 1) 
    ax.set_yscale('log')
    ax.scatter([lc['mjd_discovery']], [0.0], s = 180, marker = "D", color = 'black')
    trange = np.arange(min(tobs), max(tobs)+1, 1)

    for iwl in range(nwl):
        tobs_ = []
        fobs_ = []
        for i in range(npoint):
            if lobs[i] == wl[iwl]:
                tobs_.append(tobs[i])
                fobs_.append(fobs[i])
        ax.errorbar(tobs_, fobs_, yerr=sigma, fmt='o', color=color[iwl], label=wltag[iwl])
        if dict:
            if isbazin:
                fitb = [dict['A'], dict['T'], dict['t0'], dict['kr'], dict['kf']]
                ax.plot(trange, bazin(trange, wl[iwl], fitb), color=color[iwl])
            else:
                fite = [dict['A'], dict['T'], dict['k']]
                ax.plot(trange, expit(trange, wl[iwl], fite), color=color[iwl])

    fluxmin = max(1, np.min(fobs))
    fluxmax = np.max(fobs)
    m = math.log(fluxmin)
    M = math.log(fluxmax)
    # bracket with a bit of slack each side. Log version.
    ax.set_ylim([math.exp(1.1*m - 0.1*M), math.exp(1.1*M - .1*m)])
    ax.legend()
    if isbazin: 
        left_text  = "%s Bazin in flux" % lc['objectId']
        right_text ="T=%.1f kK (g-r=%.1f)\nkr=%.2f perday\nkf=%.2f perday" 
        right_text = right_text % (dict['T'], g_minus_r(dict['T']), dict['kr'], dict['kf'])
    else:
        left_text  = "%s Exp in flux" % lc['objectId']
        right_text ="T=%.1f kK (g-r=%.1f)\nk=%.2f perday" 
        right_text = right_text % (dict['T'], g_minus_r(dict['T']), dict['k'])

    ax.plot([0.5,1.5], [fluxmin, fluxmin*math.exp(0.25)], color='black')
    ax.text(0.8, fluxmin, '0.25 perday', fontsize=10)

    plt.title(left_text,  fontsize=16, loc='left')
    plt.title(right_text, fontsize=10, loc='right')
    plt.savefig(filename)
    plt.close(fig)

