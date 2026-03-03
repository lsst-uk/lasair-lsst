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
        distanceModulus = None
        if sherlock['classification'] in ['SN', 'NT', 'ORPHAN']:
            # use this if present
            if 'direct_distance' in sherlock:
                # Mpc to pc
                dpc = 1000000*sherlock['direct_distance']
                distanceModulus = 5*log10(dpc) - 5

            # else use measured redshift
            elif 'z' in sherlock:
                z = sherlock['z']

            # else photoZ
            elif 'photoz' in sherlock:
                z = sherlock['photoz']

            if z:
                # combine z and apparent mag to get absolute mag
                # using Ken Smith code from Atlas for distance modulus
                distances = redshiftToDistance(z)
                distanceModulus = distances['dmod']

        if not distanceModulus:
            return nothing

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
            absMag = ecMag - distanceModulus + 2.5*math.log10(1+z)
            if absMag < peakAbsMag:
                peakAbsMag = absMag
                peakMJD = lc_time[i]

        return {
            "absMag": peakAbsMag,
            "absMagMJD": peakMJD,
        }

        return 
