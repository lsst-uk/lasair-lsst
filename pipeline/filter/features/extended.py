from features.FeatureGroup import FeatureGroup
from importlib import import_module
import sys
sys.path.append("../../../common/schema/lasair_schema")
from objects import schema as objectSchema

class extended(FeatureGroup):
    _features = []
    for feature in objectSchema['ext_fields']:
        if 'name' in feature:
            _features.append(feature['name'])

    def run(self):
        out = {}
        for name in self._features:
            out[name] = self.alert['diaObject'][name]
        return out
