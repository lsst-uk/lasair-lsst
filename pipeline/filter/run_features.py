""" examples
python3 run_features.py ~/lasair-lsst/tests/unit/pipeline/filter/sample_alerts/99999999999.json
python3 run_features.py ~/lasair-lsst/tests/unit/pipeline/filter/sample_alerts/402778310355976216.json
"""
import sys, json
sys.path.append('../../common')
import settings
sys.path.append('../../common/schema/' + settings.SCHEMA_VERSION)
from features.FeatureGroup import FeatureGroup

alert_file = sys.argv[1]
alert = json.loads(open(alert_file).read())
lasair_features = FeatureGroup.run_all(alert)
s = json.dumps(lasair_features, indent=2)

out_file   = open(sys.argv[2], 'w')
out_file.write(s)
out_file.close()

