from features.FeatureGroup import FeatureGroup

class diaObjectCopy(FeatureGroup):
    """Several features are simply copied from the diaObject that Rubin provides"""

    _features = [
        'timestamp',
        'diaObjectId',
        'ra', 'decl',
        'g_psfFluxMean',
        'g_psfFluxMeanErr',
        'r_psfFluxMean',
        'r_psfFluxMeanErr',
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

        return output

