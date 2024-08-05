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
            key=lambda ds:ds['midpointMjdTai'], reverse=True)
        dict = {}
        for f in self._features:
            dict[f] = None
        for ds in diaSourcesList:
            fn = ds['band']
            fnf = fn + 'PSFlux'
            if not dict[fnf]:
                dict[fnf] = ds['psfFlux']
        if self.verbose:
            for f in self._features:
                if f not in dict:
                    print('latestFlux: %s not available' % f)
        return dict
