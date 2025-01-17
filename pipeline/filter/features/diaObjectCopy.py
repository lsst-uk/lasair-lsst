from features.FeatureGroup import FeatureGroup

class diaObjectCopy(FeatureGroup):
    """Several features are simply copied from the diaObject that Rubin provides"""

    _features = [
        'timestamp',
        'diaObjectId',
        'ra', 
        'decl',
        'pmRa', 
        'pmDec',
        'u_psfFlux',
        'u_psfFluxMean',
        'u_psfFluxMeanErr',
        'g_psfFlux',
        'g_psfFluxMean',
        'g_psfFluxMeanErr',
        'r_psfFlux',
        'r_psfFluxMean',
        'r_psfFluxMeanErr',
        'i_psfFlux',
        'i_psfFluxMean',
        'i_psfFluxMeanErr',
        'z_psfFlux',
        'z_psfFluxMean',
        'z_psfFluxMeanErr',
        'y_psfFlux',
        'y_psfFluxMean',
        'y_psfFluxMeanErr',
        'nearbyExtObj1',
        'nearbyExtObj1Sep',
        'nearbyObj1',
        'nearbyObj1Dist',
        'nearbyObj1LnP',
        'nearbyLowzGal',
        'nearbyLowzGalSep',
    ]

    def run(self):
        """Return mean flux in nJansky in all filters"""

        # copy the values from the alert
        output = {}
        object = self.alert["diaObject"]

        for f in self._features:
            if f in object:
                output[f] = object.get(f, None)
            else:
                if self.verbose: print('diaObjectCopy: did not find %s' % f)
                output[f] = None

        return output

