from .util import getFluxTimeBand
from features.FeatureGroup import FeatureGroup


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
        "lastDiaSourceMjdTai"
    ]    

    def run(self):
        (flux, time, band) = getFluxTimeBand(self.alert)
        nSource = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0}

        for b in band: nSource[b] += 1
        if self.verbose:
            print('Found %d sources' % len(time))

        lastDiaSourceMjdTai = max(time)
        nSources = len(time)

        out = { 
            "nSources": nSources,
            "nuSources": nSource['u'],
            "ngSources": nSource['g'],
            "nrSources": nSource['r'],
            "niSources": nSource['i'],
            "nzSources": nSource['z'],
            "nySources": nSource['y'],
            "lastDiaSourceMjdTai"    : lastDiaSourceMjdTai,
        }
        return out
