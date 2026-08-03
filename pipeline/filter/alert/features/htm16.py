from features.FeatureGroup import FeatureGroup
try:
    from gkhtm import _gkhtm as htmCircle
except:
    pass

class htm16(FeatureGroup):
    """Min and Max time of the diaSources"""

    _features = [
        "htm16",
    ]    

    def run(self):
        ra   = self.alert['diaObject']['ra']
        decl = self.alert['diaObject']['decl']
        try:
            htm16 = htmCircle.htmID(16, ra, decl)
        except:
            htm16 = 0
            print('WARNING: feature/htm16: Cannot compute HTM index')
        return { "htm16": htm16, }
