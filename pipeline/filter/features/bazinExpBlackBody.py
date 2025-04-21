# Fitting Bazin curves with pre-peak samples: Time-Wavelength
import sys
import json
import math
import numpy as np
from features.FeatureGroup import FeatureGroup

# these come from from https://github.com/RoyWilliams/bazinBlackBody
from bazinBlackBody import BBBEngine

class bazinExpBlackBody(FeatureGroup):
    """Min and Max time of the diaSources"""

    _features = [
        "BBBRiseRate", 
        "BBBFallRate", 
        "BBBTemp",
        "BBBPeakFlux",
        "BBBPeakAbsMag",
        "BBBPeakMJD",
    ]

    def run(self):
        fdict = {
            'BBBRiseRate': None, 
            'BBBFallRate': None,
            'BBBTemp': None, 
            'BBBPeakFlux': None,
            'BBBPeakAbsMag': None,
            'BBBPeakMJD': None,
        }

        # no whinging about overflows during normal running
        if not self.verbose:
            np.seterr(over   ='ignore')
            np.seterr(invalid='ignore')

        # only run the expensive BBB fit on 'SN', 'NT', 'ORPHAN'
#        go = False
#        try:
#            classification = self.alert['annotations']['sherlock']['classification']
#            go = (classification in ['SN', 'NT', 'ORPHAN'])
#        except:
#            return fdict
#        if not go:
#            return fdict

        BE = BBBEngine.BBB('LSST', nforced=4, A=100, T=4, t0=-6, kr=0.1, kf=0.01, verbose=False)
        try:
            (fit_e, fit_b) =  BE.make_fit(self.alert)
        except:
            return fdict

        # at some point we should put in AIC or BIC selection
        # if both fits are made
        if fit_e:
            fit = fit_e
        elif fit_b:
            fit = fit_b
            fit['k']    = fit['kr']
            fit['kerr'] = fit['krerr']
        else:
            return fdict

        fdict['BBBTemp']        = fit['T']
        fdict['BBBRiseRate']    = fit['k']
        fdict['BBBFallRate']    = fit.get('kf', None)
        fdict['BBBPeakFlux']    = fit.get('peakValue', None)
        fdict['BBBPeakAbsMag']  = None    # to be fixed later
        if 'kf' in fit:
            peakMJD = fit.get('peakTime', 0.0) + fit.get('mjd_discovery', 0.0)
            if math.isinf(peakMJD):
                fdict['BBBPeakMJD'] = None
            else:
                fdict['BBBPeakMJD'] = peakMJD

        return fdict
