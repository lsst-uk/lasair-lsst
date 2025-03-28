import math
from .util import getFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

n_sample = 10     # must be this many of given band in sample interval
t_sample = 60     # length of sample interval in days
t_test   = 10     # length of test interval in days

class jump(FeatureGroup):
    """Jump from mean of 20 days"""

    _features = [
        "jump1",
        "jump2",
    ]    

    def run(self):
        (lc_flux, lc_time, lc_band) = getFluxTimeBand(self.alert)
        fluxsum  = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0 } 
        fluxsum2 = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0 } 
        n        = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0 }
        fluxmean = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0 } 
        fluxsd   = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0 } 
        max_jump = {'u':0.0, 'g':0.0, 'r':0.0, 'i':0.0, 'z':0.0, 'y':0.0 } 

        T = lc_time[-1]   # last diaSource we know about

        for k in range(len(lc_time)):        # look back for sample
            delta = T - lc_time[k]
            # is it in the sample space
            if delta > t_test and delta < t_test + t_sample:
                f = lc_flux[k]
                band = lc_band[k]
                n[band] += 1
                fluxsum[band]  += f
                fluxsum2[band] += f*f

        for band in n.keys():
            m = n[band]
            if m < n_sample:  # enough in the sample period
                continue
            fluxmean[band] = fluxsum[band]/m
            fluxsd[band]   = math.sqrt((fluxsum2[band] - m*fluxmean[band]*fluxmean[band])/(m-1))

        for k in range(len(lc_time)):        # look back for test
            delta = T - lc_time[k]
            # is it in the test space
            if delta > 0 and delta < t_test:
                band = lc_band[k]
                if n[band] < n_sample:  # enough in the sample period
                    continue
                jmp = abs(lc_flux[k] - fluxmean[band])/fluxsd[band]
                if jmp > max_jump[band]:
                    max_jump[band] = jmp
        jumps = list(max_jump.values())
        jumps.sort()

        return { 
            "jump1": jumps[-1], 
            "jump2": jumps[-2], 
        }
