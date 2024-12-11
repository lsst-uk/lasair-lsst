import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class ebv(FeatureGroup):
    """Extinction"""

    _features = [
        "revisit_mjd",
        "revisit_colour_mag",
        "revisit_colour_bands",
        "revisit_colour_temp",
    ]    

    def run(self):
        fdict = {
            "revisit_mjd"         : None,
            "revisit_colour_mag"  : None,
            "revisit_colour_bands": None,
            "revisit_colour_temp" : None,
        }
        ra   = self.alert['diaObject']['ra']
        decl = self.alert['diaObject']['decl']

        sfd = SFDQuery()
        c = SkyCoord(ra, decl, unit="deg", frame='icrs')
        ebv = float(sfd(c))
        return fdict
