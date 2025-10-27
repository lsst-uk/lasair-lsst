from features.FeatureGroup import FeatureGroup
from importlib import import_module
import sys
import settings
sys.path.append("../../../common/schema/" + settings.SCHEMA_VERSION)
from objects import schema as objectSchema

# Copies in all the features from the diaObject
class diaObject(FeatureGroup):
    _features = []
    for feature in objectSchema['fields']:
        if 'name' in feature and feature['origin'] == 'lsst':
            _features.append(feature['name'])
    for feature in objectSchema['ext_fields']:
        if 'name' in feature:
            _features.append(feature['name'])

    def run(self):
        out = {}
        for name in self._features:
            try:
                out[name] = self.alert['diaObject'][name]
            except:
                out[name] = None

        return out
