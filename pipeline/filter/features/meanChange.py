import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class meanChange(FeatureGroup):
    """Change of mean last 10, 20 days"""

    _features = [
        "mean10change",
        "mean20change",
    ]    

    def run(self):
        return { 
            "mean10change": None, 
            "mean20change": None, 
        }
