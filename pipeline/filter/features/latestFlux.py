from features.FeatureGroup import FeatureGroup

class latestFlux(FeatureGroup):
    """Latest fluxes from the diaSources"""

    _features = [
        "uPSFlux",
        "gPSFlux",
        "rPSFlux",
        "iPSFlux",
        "zPSFlux",
        "yPSFlux",
    ]    

    def run(self):
        # sort diaSources in reverse order
        diaSourcesList = sorted(diaSourcesList, key=lambda ds:ds['midPointTai'], reverse)
        dict = {}
        for f in _features:
            dict[f] = None
        for ds in diaSourcesList:
            fn = ds['filterName']
            fnf = f + 'PSFlux'
            if not dict[fnf]:
                dict[fnf] = ds['psFlux']
            return dict
