import math
from .util import getECFluxTimeBand
from features.FeatureGroup import FeatureGroup
#from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class pair(FeatureGroup):
    """Find the most recent revisit and derive colour information"""

    _features = [
        'latestPairMJD',
        'latestPairColourMag',
        'latestPairColourBands',
        'latestPairColourTemp',
        'penultimatePairMJD',
        'penultimatePairColourMag',
        'penultimatePairColourBands',
        'penultimatePairColourTemp',
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
            try:
                magdiff = -2.5*math.log10(fluxrat)
            except:
                return None
            wl1 = WL[i1]
            wl2 = WL[i2]
            for i in range(50):
                try:
                    fr  =  blackbody(wl1, T) - fluxrat* blackbody(wl2, T)
                    dfr = dblackbody(wl1, T) - fluxrat*dblackbody(wl2, T)
                except:
                    return None
                try:
                    dT = fr/dfr
                except:
                    return None

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
            'latestPairMJD': None,
            'latestPairColourMag': None,
            'latestPairColourBands': None,
            'latestPairColourTemp': None,
            'penultimatePairMJD': None,
            'penultimatePairColourMag': None,
            'penultimatePairColourBands': None,
            'penultimatePairColourTemp': None,
        }

 # get the latest fluxes from the diaSources
        (lc_flux, lc_time, lc_band) = getECFluxTimeBand(self.alert)
        latest_done = False
        for i in range(len(lc_flux)-1, 0, -1):
            if lc_time[i] - lc_time[i-1] < 40.0/(24*60) \
                    and lc_band[i] != lc_band[i-1]:  # 40 minutes, different bands
                # found a revisit
                if not latest_done:
                    r = compute_revisit(lc_flux[i], lc_flux[i-1], lc_band[i], lc_band[i-1])
                    if r:
                        fdict['latestPairMJD']         = lc_time[i]
                        fdict['latestPairColourMag']   = r['colour_mag']
                        fdict['latestPairColourBands'] = r['colour_bands']
                        fdict['latestPairColourTemp']  = r['colour_temp']
                    latest_done = True
                else:
                    r = compute_revisit(lc_flux[i], lc_flux[i-1], lc_band[i], lc_band[i-1])
                    if r:
                        fdict['penultimatePairMJD']          = lc_time[i]
                        fdict['penultimatePairColourMag']   = r['colour_mag']
                        fdict['penultimatePairColourBands'] = r['colour_bands']
                        fdict['penultimatePairColourTemp']  = r['colour_temp']
                    break

        return fdict
