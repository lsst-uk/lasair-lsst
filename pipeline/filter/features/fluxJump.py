import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup

class fluxJump(FeatureGroup):
    """Flux jump statistic"""

    _features = [
        "fluxJump",
    ]    

    def run(self):
        days = 1 # go back a day from last diaSource
        (fobs, tobs, band) = getAllFluxTimeBand(self.alert)
        max_tobs  = tobs[-1]
        max_flux = 0
    
        dict = {'fluxJump': None}
        n = 0
        fluxsum = fluxsum2 = 0.0
        last_fobs = 0
        for i in range(len(tobs)):
            # statistics of those before 'days' days ago
            if max_tobs - tobs[i] > days:
                fluxsum  += fobs[i]
                fluxsum2 += fobs[i]*fobs[i]
                n += 1
            else:
                if fobs[i] > max_flux:
                    max_flux = fobs[i]
        if n < 4:
            if self.verbose:
                print('fluxJump: Only %d previous sources' % n)
            return dict
               
        meanf = fluxsum/n
        var = fluxsum2/n - meanf*meanf
        sd = math.sqrt(var)
        jump = (max_flux - meanf)/sd
        if jump < 0:
            jump = None
        return { 
            "fluxJump": jump, 
        }
