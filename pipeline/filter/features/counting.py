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
        "firstDiaSourceMJD",
        "lastDiaSourceMJD"
    ]    

    def run(self):
        (flux, time, band) = getFluxTimeBand(self.alert)
        nSource = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0}

        for b in band: nSource[b] += 1
        if self.verbose:
            print('Found %d sources' % len(time))
        if len(time) > 0:
            firstDiaSourceMJD = self.alert['diaObject']['firstDiaSourceMJD']
            lastDiaSourceMJD = max(time)
            nSources = len(time)
        else:
            return None

        out = { 
            "nSources": nSources,
            "nuSources": nSource['u'],
            "ngSources": nSource['g'],
            "nrSources": nSource['r'],
            "niSources": nSource['i'],
            "nzSources": nSource['z'],
            "nySources": nSource['y'],
            "firstDiaSourceMJD"   : firstDiaSourceMJD, 
            "lastDiaSourceMJD"    : lastDiaSourceMJD,
        }
        return out
