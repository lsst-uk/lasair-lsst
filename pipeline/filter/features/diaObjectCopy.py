from features.FeatureGroup import FeatureGroup

class diaObjectCopy(FeatureGroup):
    """Several features are simply copied from the diaObject that Rubin provides"""

    _features = [
        'ra', 'decl',
        'nDiaSources',
        'gPSFluxMax',
        'gPSFluxMean',
        'gPSFluxMaxSlope',
        'gPSFluxNdata',
        'rPSFluxMax',
        'rPSFluxMean',
        'rPSFluxMaxSlope',
        'rPSFluxNdata',
    ]

    def run(self):
        """Return mean flux in nJansky in all filters"""

        # copy the values from the alert
        output = {}
        object = self.alert.get("diaObject")
        for f in self._features:
            output[f] = object.get(f)
        return output

