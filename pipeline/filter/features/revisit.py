import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class revisit(FeatureGroup):
    """Find the most recent revisit and derive colour information"""

    _features = [
        "latest_revisit_mjd",
        "latest_revisit_colour_mag",
        "latest_revisit_colour_bands",
        "latest_revisit_colour_temp",
    ]    

    def run(self):
        fdict = {
            "latest_revisit_mjd"         : None,
            "latest_revisit_colour_mag"  : None,
            "latest_revisit_colour_bands": '',
            "latest_revisit_colour_temp" : None,
        }
        ra   = self.alert['diaObject']['ra']
        decl = self.alert['diaObject']['decl']

        sfd = SFDQuery()
        c = SkyCoord(ra, decl, unit="deg", frame='icrs')
        ebv = float(sfd(c))
        return fdict
