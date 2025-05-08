import math
from .util import getAllFluxTimeBand
from features.FeatureGroup import FeatureGroup
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord

class milkyWay(FeatureGroup):
    """Extinction and galactic latitude"""

    _features = [
        "ebv",
        "glat",
    ]    

    def run(self):
        ra   = self.alert['diaObject']['ra']
        decl = self.alert['diaObject']['decl']
        # https://en.wikipedia.org/wiki/Galactic_coordinate_system
        alphaNGP = 192.85948
        deltaNGP =  27.1283
        sdngp = math.sin(math.radians(deltaNGP))
        cdngp = math.cos(math.radians(deltaNGP))
        sde = math.sin(math.radians(decl))
        cde = math.cos(math.radians(decl))
        cra = math.cos(math.radians(ra - alphaNGP))
        glat = math.degrees(math.asin(sdngp*sde + cdngp*cde*cra))

        return { 
            "ebv": self.alert['ebv'],
            "glat": glat,
        }
