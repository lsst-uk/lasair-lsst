# Fitting Bazin curves with pre-peak samples: Time-Wavelength
import sys
import json
import math
import numpy as np
from .redshift import redshiftToDistance
from .BBBEngine import BBB
from features.FeatureGroup import FeatureGroup

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

        # only run the expensive BBB fit on some
        try:
            sherlock = self.alert['annotations']['sherlock'][0]
            if not sherlock['classification'] in ['SN', 'NT', 'ORPHAN']:
                return fdict
        except:
            sherlock = None

        BE = BBB('LSST', nforced=4, ebv=self.alert['ebv'], \
                A=100, T=4, t0=6, kr=0.1, kf=0.01)
        fit =  BE.make_fit(self.alert)
#        if fit:
#            filename = '/home/ubuntu/lsst_alerts2/' + str(self.alert['diaObjectId']) + 'a'
#            BE.plot(self.alert, fit, filename)

        if not fit:
            BE = BBB('LSST', nforced=4, ebv=self.alert['ebv'], \
                A=1000, T=4, t0=-5, kr=0.01, kf=0.01)
            fit =  BE.make_fit(self.alert)
#            if fit:
#                filename = '/home/ubuntu/lsst_alerts2/' + str(self.alert['diaObjectId']) + 'b'
#                BE.plot(self.alert, fit, filename)
        if not fit:
            return fdict

        fdict['BBBTemp']        = fit['T']
        fdict['BBBRiseRate']    = fit['k']
        fdict['BBBFallRate']    = fit.get('kf', None)
        fdict['BBBPeakFlux']    = fit.get('peakValue', None)

        # no peak for exp fit, only for bazin
        if 'kf' in fit:
            peakMJD = fit.get('peakTime', 0.0) + fit.get('mjd_discovery', 0.0)
            if not math.isinf(peakMJD):
                fdict['BBBPeakMJD'] = peakMJD

        # abs mag if there is a redshift
        z = None
        if sherlock:
            if 'z' in sherlock:        z = sherlock['z']
            elif 'photoz' in sherlock: z = sherlock['photoz']
            if z and fdict['BBBPeakFlux'] and fdict['BBBPeakFlux'] > 0:
                distances = redshiftToDistance(z)
                distanceModulus = distances['dmod']
                ecMag = 31.4 - 2.5*math.log10(fdict['BBBPeakFlux'])
                fdict['BBBPeakAbsMag'] = ecMag - distanceModulus + 2.5*math.log(1+z)

        return fdict
