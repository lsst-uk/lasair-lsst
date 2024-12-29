import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class periodic(FeatureGroup):
    """Periodic behaviour"""

    _features = [
        "period",
        "period_entropy",
    ]    

    def run(self):
        return { 
            "period": None, 
            "period_entropy": None,
        }
