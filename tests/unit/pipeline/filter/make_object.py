import sys, json
from modify_alert import modify

sys.path.append('../../../../common')
import settings
sys.path.append('../../../../pipeline/filter')
sys.path.append('../../../../common/schema/' + settings.SCHEMA_VERSION)
import features
from features import *
from features.FeatureGroup import FeatureGroup
print('using schema', settings.SCHEMA_VERSION)

if len(sys.argv) > 1:
    sample = sys.argv[1]
else:
    print('Usage: make_object.py <file>')
    print('... looks for sample_alert/<file>.json')
    sys.exit()

with open("sample_alerts/%s.json"%sample) as fin:
      alert = modify(json.load(fin))
      output = FeatureGroup.run_all(alert, verbose=False)
      with open("sample_alerts/%s_object.json"%sample, 'w') as fout:
          fout.write(json.dumps(output, indent=2))

