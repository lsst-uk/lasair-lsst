# Fitting Bazin curves with pre-peak samples: Time-Wavelength

import math
import numpy as np

# these come from from https://github.com/RoyWilliams/BBB
import BBB.settings_bbb
import BBB.runBBB
import BBB.coreBBB

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

        dict = BBB.runBBB.run(self.alert)
        if not dict:
            return fdict
        if 'kr' in dict:
            dict['k'] = dict['kr']
            dict['kerr'] = dict['krerr']
        fdict['bazinExpTemp']        = dict['T']
        fdict['bazinExpRiseRate']    = dict['k']
        fdict['bazinExpFallRate']    = dict.get('kf', None)
        fdict['bazinExpTempErr']     = dict['Terr']
        fdict['bazinExpRiseRateErr'] = dict['kerr']
        fdict['bazinExpFallRateErr'] = dict.get('kferr', None)
        return fdict
