import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class milkyWay(FeatureGroup):
    """Extinction and glacatic latitude"""

    _features = [
        "ebv",
        "glat",
    ]    

    def run(self):
        ra   = self.alert['diaObject']['ra']
        decl = self.alert['diaObject']['decl']

        sfd = SFDQuery()
        c = SkyCoord(ra, decl, unit="deg", frame='icrs')
        ebv = float(sfd(c))
        return { 
            "ebv": ebv, 
            "glat": None,
        }
