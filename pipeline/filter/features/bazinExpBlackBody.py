# Fitting Bazin curves with pre-peak samples: Time-Wavelength

import math
import numpy as np
from .util import getMostFluxTimeBand

wl = {
    'u':0.380,
    'g':0.500,
    'r':0.620,
    'i':0.740,
    'z':0.880,
    'y':1.000,
    }

# coreBBB should be the file from https://github.com/RoyWilliams/BBB
from .BBB.coreBBB import fit_expit, fit_bazin

def fitBazinExpBB(alert, pexpit0, pbazin0, sigma):
    empty = {
        'bazinExpTemp': None, 'bazinExpRiseRate': None, 'bazinExpFallRate': None,
        'bazinExpTempErr': None, 'bazinExpRiseRateErr': None, 'bazinExpFallRateErr': None,
    }
    if len(alert['diaSourcesList']) < 4:
        return empty

    (flux, time, band) = getMostFluxTimeBand(alert)

    # BBB wants wavelength in microns
    lobs = [wl[b] for b in band]
    sources = sorted(alert['diaSourcesList'],
        key=lambda source: source['midpointMjdTai'])

    # BBB wants times relative to time for first diaSource
    mjd_discovery = sources[0]['midpointMjdTai']
    tobs = [t-mjd_discovery for t in time]
    

    (Rsqe, dicte) = fit_expit(tobs, lobs, flux, pexpit0, sigma)
    (Rsqb, dictb) = fit_bazin(tobs, lobs, flux, pbazin0, sigma)
    if dicte and dictb:
        if Rsqe < Rsqb: return dicte
        else:           return dictb
    elif dicte:
        return dicte
    elif dictb:
        return dictb
    else:
        return empty

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

        # no whinging about overflows during normal running
        if not self.verbose:
            np.seterr(over   ='ignore')
            np.seterr(invalid='ignore')

        dict = fitBazinExpBB(self.alert, pexpit0, pbazin0, sigma)
        return dict
