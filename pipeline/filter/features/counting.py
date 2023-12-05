from .util import getFluxTimeBand
from features.FeatureGroup import FeatureGroup

nSource = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0}

class counting(FeatureGroup):
    """Counts of sources plus Min and Max time of the diaSources"""

    _features = [
        "nSources",
        "nuSources",
        "ngSources",
        "nrSources",
        "niSources",
        "nzSources",
        "nySources",
        "minTai",
        "maxTai"
    ]    

    def run(self):
        (flux, time, band) = getFluxTimeBand(self.alert)

        for b in band: nSource[b] += 1
        if self.verbose:
            print('Found %d sources' % len(time))
        return { 
            "nSources": len(time),
            "nuSources": nSource['u'],
            "ngSources": nSource['g'],
            "nrSources": nSource['r'],
            "niSources": nSource['i'],
            "nzSources": nSource['z'],
            "nySources": nSource['y'],
            "minTai"  : min(time), 
            "maxTai"  : max(time),
        }
