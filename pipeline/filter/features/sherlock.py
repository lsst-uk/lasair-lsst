import math
from .util import getECFluxTimeBand
from .redshift import redshiftToDistance
from features.FeatureGroup import FeatureGroup

class sherlock(FeatureGroup):
    """Extinction"""

    _features = [
        "absMag",
        "absMagMJD",
    ]    

    def run(self):
        nothing = { 
            "absMag": None, 
            "absMagMJD": None, 
        }

        try:
            sherlock = self.alert['annotations']['sherlock'][0]
        except:
            return nothing

        z = None
        if sherlock['classification'] in ['SN', 'NT', 'ORPHAN']:
            if 'z' in sherlock:
                z = sherlock['z']
            elif 'photoz' in sherlock:
                z = sherlock['photoz']
        if not z:
            return nothing

        # combine z and apparent mag to get absolute mag
        # using Ken Smith code from Atlas for distance modulus
        distances = redshiftToDistance(z)
        distanceModulus = distances['dmod']

        # extinction corrected lightcurve
        (lc_ecflux, lc_time, lc_band) = getECFluxTimeBand(self.alert)
        peakAbsMag = 99
        peakMJD    = 99
        for i in range(len(lc_ecflux)):
            # flux in nanoJ
            try:
                ecMag = 31.4 - 2.5*math.log10(lc_ecflux[i])
            except:
                continue
            absMag = ecMag - distanceModulus + 2.5*math.log(1+z)
            if absMag < peakAbsMag:
                peakAbsMag = absMag
                peakMJD = lc_time[i]

        return {
            "absMag": peakAbsMag,
            "absMagMJD": peakMJD,
        }

        return 
