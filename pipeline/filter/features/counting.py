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

        try:  # supposed to be in the alert when Eric gets round to it
            firstDiaSourceMJD = self.alert['diaObject']['firstDiaSourceMJD']
        except:
            firstDiaSourceMJD = 999.0

        lastDiaSourceMJD = max(time)
        nSources = len(time)

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
