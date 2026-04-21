""" examples
python3 run_features.py ~/lasair-lsst/tests/unit/pipeline/filter/sample_alerts/
BE CAREFUL THIS CHANGES THE FILES IN THE TEST SUITE
"""
import sys, json, os
sys.path.append('../../common')
import settings
sys.path.append('../../common/schema/' + settings.SCHEMA_VERSION)
from features.FeatureGroup import FeatureGroup
from filters import lightcurve_lite

if len(sys.argv) > 1:
    dir = sys.argv[1]
else:
    print('Usage: run_features <sample_alert_directory>')
    sys.exit()

for file in os.listdir(dir):
    if not file.endswith('.json'): continue
    if file.endswith('object.json'): continue
    if file.endswith('lite.json'): continue
    name = file.split('.')[0]
    alert_file = dir +'/'+ name + '.json'

    object_file   = dir +'/'+ name + '_object.json'
#    print(alert_file)
    alert = json.loads(open(alert_file).read())
    lasair_features = FeatureGroup.run_all(alert)
    s = json.dumps(lasair_features, indent=2)
#    print(s)
#    print('===')
    f = open(object_file, 'w')
    f.write(s)
    f.close()

    lite_file   = dir +'/'+ name + '_lite.json'
    lite = lightcurve_lite(alert)
    f = open(lite_file, 'w')
    s = json.dumps(lite, indent=2)
    f.write(s)
    f.close()

