""" Computes Fastfinder features
    Ported from https://github.com/mFulton07/LasairFastfinder

    To run this code:
    $ cd ../../../tests/unit/pipeline/filter/
    $ python3 run_feature.py

    To look at the sample alert:
    $ cat ../../../tests/unit/pipeline/filter/sample_alerts/lsst1.json
"""

from features.FeatureGroup import FeatureGroup

filterNames = ['u', 'g', 'r', 'i', 'z', 'y']

class fastfinder(FeatureGroup):
    _features = [
        "uIncline", "uInclineErr", 
        "gIncline", "gInclineErr", 
        "rIncline", "rInclineErr", 
        "iIncline", "iInclineErr", 
        "zIncline", "zInclineErr", 
        "yIncline", "yInclineErr",
    ]    

    def run(self):
        diaSources            = self.alert['diaSourcesList']
        diaForcedSources      = self.alert['diaForcedSourcesList']
        diaNondetectionLimits = self.alert['diaNondetectionLimitsList']

        ret = {}
        for filterName in filterNames:
            ret[filterName+'Incline']    = 42
            ret[filterName+'InclineErr'] = 0.42
        return ret
