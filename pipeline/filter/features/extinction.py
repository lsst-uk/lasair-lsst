import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class extinction(FeatureGroup):
    """Extinction"""

    _features = [
        "ebv",
    ]    

    def run(self):
        ra   = self.alert['diaObject']['ra']
        decl = self.alert['diaObject']['decl']

        sfd = SFDQuery()
        c = SkyCoord(ra, decl, frame='icrs')
        ebv = sfd(c)
        return { 
            "ebv": ebv, 
        }
