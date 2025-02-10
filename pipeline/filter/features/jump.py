import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class jump(FeatureGroup):
    """Jump from mean of 20 days"""

    _features = [
        "jumpFromMean20",
    ]    

    def run(self):
        return { 
            "jumpFromMean20": None, 
        }
