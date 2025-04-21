import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class sherlock(FeatureGroup):
    """Extinction"""

    _features = [
        "absMag",
        "absMagMJD",
    ]    

    def run(self):
        return { 
            "absMag": None, 
            "absMagMJD": None, 
        }
