import statistics
from .util import getFluxTimeBand, getReliability
from features.FeatureGroup import FeatureGroup


class counting(FeatureGroup):
    """Counts of sources plus Min and Max time of the diaSources"""

    _features = [
        "medianR",
        "latestR",
        "nSourcesGood",
        "nuSources",
        "ngSources",
        "nrSources",
        "niSources",
        "nzSources",
        "nySources",
        "lastDiaSourceMjdTai",
        "firstDiaSourceMjdTai",
    ]    

    def run(self):
        (flux, time, band) = getFluxTimeBand(self.alert)
        reliability = getReliability(self.alert)
        medianR = statistics.median(reliability)
        latestR = reliability[-1]    # last one
        nSourcesGood = 0
        for r in reliability:
            if r > 0.5:
                nSourcesGood += 1

        nSource = {'u':0, 'g':0, 'r':0, 'i':0, 'z':0, 'y':0}

        for b in band: nSource[b] += 1
        if self.verbose:
            print('Found %d sources' % len(time))

        out = { 
            "medianR":      medianR,
            "latestR":      latestR,
            "nSourcesGood": nSourcesGood,
            "nuSources":    nSource['u'],
            "ngSources":    nSource['g'],
            "nrSources":    nSource['r'],
            "niSources":    nSource['i'],
            "nzSources":    nSource['z'],
            "nySources":    nSource['y'],
            "lastDiaSourceMjdTai" : max(time),
        }

        # if rubin didn't set this, just use the first that we have in the lightcurve
        if not "firstDiaSourceMjdTai" in self.alert or math.isnan(self.alert["firstDiaSourceMjdTai"]):
            out["firstDiaSourceMjdTai"] = min(time)

        return out
