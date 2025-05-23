import json, sys, numpy
from .BBBCore import *
WL    = [0.380,     0.500,     0.620,     0.740,     0.880,     1.000, ]
BANDS = ['u',       'g',       'r'  ,     'i'  ,     'z'  ,     'y'    ]

def mag2flux(mag, magerr, magzpsci):
    # flux in microJ
    flux =  math.pow(10, (magzpsci-mag)/2.5)
    fluxerr = magerr * flux * 0.92  # ln(10)/2.5
    return (flux, fluxerr)

# The LSST bands
EXTCOEF   = {'u':4.145, 'g':3.237, 'r':2.273, 'i':1.684, 'z':1.323, 'y':1.088}

# Modify magnitude for extinction
def dustmag(mag, band, ebv):
    return mag - ebv*EXTCOEF[band]
def dustflux(flux, band, ebv):
    return flux*math.pow(10, ebv*EXTCOEF[band]/2.5)

class BBB():
    def __init__(self, survey, nforced=4, ebv=0.0, A=10000, T=8, t0=-6, kr=1, kf=0.1, verbose=False):
        self.is_lsst = (survey == 'LSST')
        self.ebv = ebv
        self.pexpit0 = [A, T, kr-kf]
        self.pbazin0 = [A, T, t0, kr, kf]
        self.nforced = nforced
        self.verbose = verbose
        np.seterr(all="ignore")

    def read_alert(self, alert):
        if self.is_lsst:
            objectId = alert['diaObject']['diaObjectId']
            sources  = alert['diaSourcesList']
            forced   = alert['diaForcedSourcesList']
            mjdkey   = 'midpointMjdTai'
            bandkey  = 'band'
        else:
            objectId = alert['objectId']
            sources  = [c for c in alert['candidates'] if 'candid' in c]
            forced   = alert['forcedphot']
            mjdkey   = 'mjd'
            bandkey  = 'fid'
    
        lc = {
            'objectId': objectId,
            'mjd_discovery': 0,
            't':        [],  # days after discovery
            'bandindex':[],  # index of the waveband
            'flux':     [],  # flux in microJ or nanoJ
            'fluxerr':  []
             }
        lc['TNS'] = alert.get('TNS', None)
    
        sources.sort(key = lambda c: c[mjdkey])
        lc['mjd_discovery'] = sources[0][mjdkey]
    
        if len(sources) < 5:
            return None
        if self.verbose:
            print('%s has %s' % (objectId, len(sources)))
        for c in sources:
            if self.is_lsst:
                # correct for extinction in case of LSST
                band = c['band']
                flux = dustflux(c['psfFlux'], band, self.ebv)
                lc['bandindex'].append(BANDS.index(band))
                (flux, fluxerr) = (flux, c['psfFluxErr'])
            else:
                lc['bandindex'].append(c['fid'])
                (flux, fluxerr) = mag2flux(c['magpsf'], c['sigmapsf'], c['magzpsci'])
    
            lc['t']      .append(c[mjdkey] - lc['mjd_discovery'])
            lc['flux']   .append(flux)
            lc['fluxerr'].append(fluxerr)
    
        lc['post_discovery'] = lc['t'][-1]
            
    # try to prepend with some forced phot points    
        forced.sort(key = lambda f: f[mjdkey])
    # see if we can find four forced phot points before first detection
        nforced = self.nforced
    
        nforced_found = 0
        for ii in range(len(forced)): # go backwards just past discovery
            i = len(forced)-ii-1
            f = forced[i]
            if f[mjdkey] < lc['mjd_discovery']:
                t = f[mjdkey]-lc['mjd_discovery']
                lc['t'].insert(0, t)
                if self.is_lsst:
                    # correct for extinction in case of LSST
                    band = f['band']
                    flux = dustflux(f['psfFlux'], band, self.ebv)
                    lc['bandindex'].insert(0, BANDS.index(f[bandkey]))
                    (flux, fluxerr) = (flux, f['psfFluxErr'])
                else:
                    lc['bandindex'].insert(0, f[bandkey])
                    (flux, fluxerr) = (f['forcediffimflux'], f['forcediffimfluxunc'])
                lc['flux'].insert(0, flux)
                lc['fluxerr'].insert(0, fluxerr)
                nforced_found += 1
                if nforced_found >= nforced:
                    break
        return lc
    
    def make_fit(self, alert):
        # extract the lightcurve as a time-wavelenght surface
        lc = self.lc = self.read_alert(alert)
        if not lc:
            return (None, None)
    
        tobs = lc['t']
        lobs = [WL[i] for i in lc['bandindex']]
        fobs = lc['flux']
        npoint = len(lc['t'])
        objectId = lc['objectId']
    
        dicte = fit_expit(tobs, lobs, fobs, self.pexpit0, verbose=self.verbose)
        if dicte:
            if self.verbose:
                print('Expit: T= %.2f (g-r=%.3f), k=%.3f' % \
                    (dicte['T'], g_minus_r(dicte['T']), dicte['k']))
            dicte['post_discovery'] = lc['post_discovery']
            dicte['mjd_discovery'] = lc['mjd_discovery']
            try:
                dicte['tns_name'] = lc['TNS']['tns_prefix'] +' '+ lc['TNS']['tns_name']
            except:
                dicte['tns_name'] = ''
    
        dictb = fit_bazin(tobs, lobs, fobs, self.pbazin0, verbose=self.verbose)
        if dictb:
            if self.verbose:
                print('Bazin: T=%.2f (g-r=%.3f), kr=%.3f, kf=%.3f' % \
                    (dictb['T'],  g_minus_r(dictb['T']), dictb['kr'], dictb['kf']))
            dictb['post_discovery'] = lc['post_discovery']
            dictb['mjd_discovery'] = lc['mjd_discovery']
            try:
                dictb['tns_name'] = lc['TNS']['tns_prefix'] +' '+ lc['TNS']['tns_name']
            except:
                dictb['tns_name'] = ''
    
        return (dicte, dictb)

    def plot(self, alert, dictx, filename):

        lc = self.lc
        isbazin = ('kr' in dictx)
        npoint = len(lc['t'])
        tobs = lc['t']
        fobs = lc['flux']
        
        plt.rcParams.update({'font.size': 8})
        fig = plt.figure(figsize=(6,6))
        ax = plt.subplot(1, 1, 1)
        ax.set_yscale('log')
        ax.scatter([0.0], [0.0], s = 180, marker = "D", color = 'black')
        trange = np.arange(min(tobs), max(tobs)+1, 1)
        
        for iwl in range(nwl):
            tobs_ = []
            fobs_ = []
            for i in range(npoint):
                if lc['bandindex'][i] == iwl:
                    tobs_.append(tobs[i])
                    fobs_.append(fobs[i])
            ax.errorbar(tobs_, fobs_, yerr=sigma, fmt='o', color=color[iwl], label=BANDS[iwl])
            if dictx:
                if isbazin:
                    fitb = [dictx['A'], dictx['T'], dictx['t0'], dictx['kr'], dictx['kf']]
                    ax.plot(trange, bazin(trange, WL[iwl], fitb), color=color[iwl])
                else:
                    fite = [dictx['A'], dictx['T'], dictx['k']]
                    ax.plot(trange, expit(trange, WL[iwl], fite), color=color[iwl])
    
        fluxmin = max(1, np.min(fobs))
        fluxmax = np.max(fobs)
        m = math.log(fluxmin)
        M = math.log(fluxmax)
        # bracket with a bit of slack each side. Log version.
        ax.set_ylim([math.exp(1.1*m - 0.1*M), math.exp(1.1*M - .1*m)])
        ax.legend()
        isbazin = ('kr' in dictx)
        if isbazin:
            left_text  = "%s Bazin in flux" % lc['objectId']
            right_text ="T=%.1f kK (g-r=%.1f)\nkr=%.2f perday\nkf=%.2f perday"
            right_text = right_text % (dictx['T'], g_minus_r(dictx['T']), dictx['kr'], dictx['kf'])
        else:
            left_text  = "%s Exp in flux" % lc['objectId']
            right_text ="T=%.1f kK (g-r=%.1f)\nk=%.2f perday"
            right_text = right_text % (dictx['T'], g_minus_r(dictx['T']), dictx['k'])
    
        ax.plot([0.5,1.5], [fluxmin, fluxmin*math.exp(0.25)], color='black')
        ax.text(0.8, fluxmin, '0.25 perday', fontsize=10)
    
        plt.title(left_text,  fontsize=16, loc='left')
        plt.title(right_text, fontsize=10, loc='right')
        plt.savefig(filename)
        plt.close(fig)
        npoint = len(lc['t'])
        tobs = lc['t']
        fobs = lc['flux']
        
        plt.rcParams.update({'font.size': 8})
        fig = plt.figure(figsize=(6,6))
        ax = plt.subplot(1, 1, 1)
        ax.set_yscale('log')
        ax.scatter([0.0], [0.0], s = 180, marker = "D", color = 'black')
        trange = np.arange(min(tobs), max(tobs)+1, 1)
        
        for iwl in range(len(WL)):
            tobs_ = []
            fobs_ = []
            for i in range(npoint):
                if lc['bandindex'][i] == iwl:
                    tobs_.append(tobs[i])
                    fobs_.append(fobs[i])
            ax.errorbar(tobs_, fobs_, yerr=sigma, fmt='o', color=color[iwl], label=BANDS[iwl])
            if dictx:
                if isbazin:
                    fitb = [dictx['A'], dictx['T'], dictx['t0'], dictx['kr'], dictx['kf']]
                    ax.plot(trange, bazin(trange, WL[iwl], fitb), color=color[iwl])
                else:
                    fite = [dictx['A'], dictx['T'], dictx['k']]
                    ax.plot(trange, expit(trange, WL[iwl], fite), color=color[iwl])
    
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
            right_text = right_text % (dictx['T'], g_minus_r(dictx['T']), dictx['kr'], dictx['kf'])
        else:
            left_text  = "%s Exp in flux" % lc['objectId']
            right_text ="T=%.1f kK (g-r=%.1f)\nk=%.2f perday"
            right_text = right_text % (dictx['T'], g_minus_r(dictx['T']), dictx['k'])
    
        ax.plot([0.5,1.5], [fluxmin, fluxmin*math.exp(0.25)], color='black')
        ax.text(0.8, fluxmin, '0.25 perday', fontsize=10)
    
        plt.title(left_text,  fontsize=16, loc='left')
        plt.title(right_text, fontsize=10, loc='right')
        plt.savefig(filename)
        plt.close(fig)
