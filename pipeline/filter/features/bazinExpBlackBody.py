# Fitting Bazin curves with pre-peak samples: Time-Wavelength
import sys
import json
import math
import numpy as np
from features.FeatureGroup import FeatureGroup

# these come from from https://github.com/RoyWilliams/BBB
sys.path.append('/home/ubuntu/BBB')
from BBB import BBBEngine

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
        fdict = {
            'bazinExpTemp': None, 
            'bazinExpRiseRate': None, 
            'bazinExpFallRate': None,
            'bazinExpTempErr': None, 
            'bazinExpRiseRateErr': None, 
            'bazinExpFallRateErr': None,
        }

        # no whinging about overflows during normal running
        if not self.verbose:
            np.seterr(over   ='ignore')
            np.seterr(invalid='ignore')

        # only run the expensive BBB fit on 'SN', 'NT', 'ORPHAN'
        go = False
        try:
            classification = self.alert['annotations']['sherlock']['classification']
            go = (classification in ['SN', 'NT', 'ORPHAN'])
        except:
            return fdict
        if not go:
            return fdict

        BE = BBBEngine.BBB('LSST', verbose=False)
        (fit_e, fit_b) =  BE.make_fit(self.alert)
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

        fdict['bazinExpTemp']        = fit['T']
        fdict['bazinExpRiseRate']    = fit['k']
        fdict['bazinExpFallRate']    = fit.get('kf', None)
        fdict['bazinExpTempErr']     = fit['Terr']
        fdict['bazinExpRiseRateErr'] = fit['kerr']
        fdict['bazinExpFallRateErr'] = fit.get('kferr', None)
        return fdict
