""" examples
python3 run_features.py ~/lasair-lsst/tests/unit/pipeline/filter/sample_alerts/99999999999.json
python3 run_features.py ~/lasair-lsst/tests/unit/pipeline/filter/sample_alerts/402778310355976216.json
"""
import sys, json, os
sys.path.append('../../common')
import settings
sys.path.append('../../common/schema/' + settings.SCHEMA_VERSION)
from features.FeatureGroup import FeatureGroup

dir = '/home/ubuntu/lasair-lsst/tests/unit/pipeline/filter/sample_alerts'

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
