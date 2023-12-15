from features.FeatureGroup import FeatureGroup

class diaObjectCopy(FeatureGroup):
    """Several features are simply copied from the diaObject that Rubin provides"""

    _features = [
        'diaObjectId',
        'ra', 'decl',
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
        object = self.alert["diaObject"]

        for f in self._features:
            if f in object:
                output[f] = object[f]
            else:
                if self.verbose: print('diaObjectCopy: did not find %s' % f)
                output[f] = None

        # because of a mistake in the DP0.2 schema
        if output['gPSFluxNdata']: output['gPSFluxNdata'] = int(output['gPSFluxNdata'])
        else                     : output['gPSFluxNdata'] = None
        if output['rPSFluxNdata']: output['rPSFluxNdata'] = int(output['rPSFluxNdata'])
        else                     : output['rPSFluxNdata'] = None
        return output

