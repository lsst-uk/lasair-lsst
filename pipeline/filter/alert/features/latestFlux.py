from features.FeatureGroup import FeatureGroup
from .util import getFluxTimeBand

class latestFlux(FeatureGroup):
    _features = [
        'u_psfFlux', 'u_latestMJD',
        'g_psfFlux', 'g_latestMJD',
        'r_psfFlux', 'r_latestMJD',
        'i_psfFlux', 'i_latestMJD',
        'z_psfFlux', 'z_latestMJD',
        'y_psfFlux', 'y_latestMJD',
        'latest_psfFlux'
    ]

    def run(self):
        """Return latest flux in nJansky in all filters"""

        # get the latest fluxes from the diaSources
        output = {}
        (lc_flux, lc_time, lc_band) = getFluxTimeBand(self.alert)
        for band in ['u', 'g', 'r', 'i', 'z', 'y']:
            bandflux  = band + '_psfFlux'
            latestMJD = band + '_latestMJD'
            output[bandflux] = None
            output[latestMJD] = None
            for i in range(len(lc_flux)-1, -1, -1):
                if lc_band[i] == band:
                    output[bandflux]  = lc_flux[i]
                    output[latestMJD] = lc_time[i]
        output['latest_psfFlux'] = lc_flux[-1]

        return output

