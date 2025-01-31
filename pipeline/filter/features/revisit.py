import math
from .util import getFluxTimeBand
from features.FeatureGroup import FeatureGroup
#from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class revisit(FeatureGroup):
    """Find the most recent revisit and derive colour information"""

    _features = [
        "latest_rv_mjd",
        "latest_rv_colour_mag",
        "latest_rv_colour_bands",
        "latest_rv_colour_temp",
        "penultimate_rv_mjd",
        "penultimate_rv_colour_mag",
        "penultimate_rv_colour_bands",
        "penultimate_rv_colour_temp",
    ]    


    def run(self):
        def blackbody(wl, T):
            hck = 14.387
            q = math.exp(hck/(wl*T))
            return math.pow(wl, -3.0) /(q - 1)

        def dblackbody(wl, T):
            hck = 14.387
            q = math.exp(hck/(wl*T))
            return math.pow(wl, -3.0) * (hck/(wl*T*T)) * q/((q-1)*(q-1))

        def compute_revisit(flux1, flux2, band1, band2):
#            print('revisit:', flux1/flux2, band1, band2)
            # The LSST bands, wavelength in microns
            WL    = [0.380, 0.500, 0.620, 0.740, 0.880, 1.000, ]
            BANDS = ['u',   'g',   'r',   'i',   'z',   'y'    ]
            i1 = BANDS.index(band1)
            i2 = BANDS.index(band2)
            if i1<i2:
                fluxrat = flux1/flux2
            else:
                (i1,i2)=(i2,i1)
                fluxrat = flux2/flux1
                T = 12  # guess 12,000 kelvin
            magdiff = -2.5*math.log10(fluxrat)
            wl1 = WL[i1]
            wl2 = WL[i2]
            for i in range(50):
                try:
                    fr  =  blackbody(wl1, T) - fluxrat* blackbody(wl2, T)
                    dfr = dblackbody(wl1, T) - fluxrat*dblackbody(wl2, T)
                except:
                    return None
                dT = fr/dfr
                T = T - dT
                if abs(dT) < 0.001: 
                    ret = {
                        'colour_mag'  : magdiff,
                        'colour_bands': '%s-%s' % (BANDS[i1], BANDS[i2]),
                        'colour_temp' : T
                    }
                    return ret # convergence

                if T < 0: return None  # not interested in negative temperatures
            return None

        fdict = {
            'latest_rv_mjd'         : None,
            'latest_rv_colour_mag'  : None,
            'latest_rv_colour_bands': '',
            'latest_rv_colour_temp' : None,
            'penultimate_rv_mjd'         : None,
            'penultimate_rv_colour_mag'  : None,
            'penultimate_rv_colour_bands': '',
            'penultimate_rv_colour_temp' : None,
        }
#        ra   = self.alert['diaObject']['ra']
#        decl = self.alert['diaObject']['decl']
#        sfd = SFDQuery()
#        c = SkyCoord(ra, decl, unit='deg', frame='icrs')
#        ebv = float(sfd(c))


 # get the latest fluxes from the diaSources
        (lc_flux, lc_time, lc_band) = getFluxTimeBand(self.alert)
        latest_done = False
        for i in range(len(lc_flux)-1, 0, -1):
            if lc_time[i] - lc_time[i-1] < 40.0/(24*60):  # 40 minutes
                # found a revisit
                if not latest_done:
                    r = compute_revisit(lc_flux[i], lc_flux[i-1], lc_band[i], lc_band[i-1])
                    if r:
                        fdict['latest_rv_mjd']          = lc_time[i]
                        fdict['latest_rv_colour_mag']   = r['colour_mag']
                        fdict['latest_rv_colour_bands'] = r['colour_bands']
                        fdict['latest_rv_colour_temp']  = r['colour_temp']
                    latest_done = True
                else:
                    r = compute_revisit(lc_flux[i], lc_flux[i-1], lc_band[i], lc_band[i-1])
                    if r:
                        fdict['penultimate_rv_mjd']          = lc_time[i]
                        fdict['penultimate_rv_colour_mag']   = r['colour_mag']
                        fdict['penultimate_rv_colour_bands'] = r['colour_bands']
                        fdict['penultimate_rv_colour_temp']  = r['colour_temp']
                    break

        return fdict
