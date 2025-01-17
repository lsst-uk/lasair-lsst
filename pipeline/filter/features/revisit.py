import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
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
        fdict = {
            "latest_rv_mjd"         : None,
            "latest_rv_colour_mag"  : None,
            "latest_rv_colour_bands": '',
            "latest_rv_colour_temp" : None,
            "penultimate_rv_mjd"         : None,
            "penultimate_rv_colour_mag"  : None,
            "penultimate_rv_colour_bands": '',
            "penultimate_rv_colour_temp" : None,
        }
        ra   = self.alert['diaObject']['ra']
        decl = self.alert['diaObject']['decl']

        sfd = SFDQuery()
        c = SkyCoord(ra, decl, unit="deg", frame='icrs')
        ebv = float(sfd(c))
        return fdict
