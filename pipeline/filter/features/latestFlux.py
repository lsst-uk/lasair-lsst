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
        diaSourcesList = sorted(self.alert['diaSourcesList'], 
            key=lambda ds:ds['midPointTai'], reverse=True)
        dict = {}
        for f in self._features:
            dict[f] = None
        for ds in diaSourcesList:
            fn = ds['filterName']
            fnf = fn + 'PSFlux'
            if not dict[fnf]:
                dict[fnf] = ds['psFlux']
            return dict
