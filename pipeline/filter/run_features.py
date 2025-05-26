""" examples
python3 run_features.py ~/lasair-lsst/tests/unit/pipeline/filter/sample_alerts/
BE CAREFUL THIS CHANGES THE FILES IN THE TEST SUITE
"""
import sys, json, os
sys.path.append('../../common')
import settings
sys.path.append('../../common/schema/' + settings.SCHEMA_VERSION)
from features.FeatureGroup import FeatureGroup

if len(sys.argv) > 1:
    dir = sys.argv[1]
else:
    print('Usage: run_features <sample_alert_directory>')
    sys.exit()

for file in os.listdir(dir):
    if not file.endswith('.json'): continue
    if file.endswith('object.json'): continue
    name = file.split('.')[0]
    alert_file = dir +'/'+ name + '.json'
    out_file   = dir +'/'+ name + '_object.json'
    print(alert_file)
    alert = json.loads(open(alert_file).read())
    lasair_features = FeatureGroup.run_all(alert)
    s = json.dumps(lasair_features, indent=2)
    f = open(out_file, 'w')
    f.write(s)
    f.close()
