from features.FeatureGroup import FeatureGroup
from .util import getFluxTimeBand

class latestFlux(FeatureGroup):
    _features = [
        'u_psfFlux',
        'g_psfFlux',
        'r_psfFlux',
        'i_psfFlux',
        'z_psfFlux',
        'y_psfFlux',
    ]

    def run(self):
        """Return latest flux in nJansky in all filters"""

        # get the latest fluxes from the diaSources
        output = {}
        (lc_flux, lc_time, lc_band) = getFluxTimeBand(self.alert)
        for band in ['u', 'g', 'r', 'i', 'z', 'y']:
            bandflux = band + '_psfFlux'
            output[bandflux] = None
            for i in range(len(lc_flux)-1, -1, -1):
                if lc_band[i] == band:
                    output[bandflux] = lc_flux[i]

        return output

