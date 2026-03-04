import sys
import math
import context
import unittest.main
from unittest import TestCase
import json
sys.path.append('../../../../common')
import settings
sys.path.append('../../../../pipeline/filter')
sys.path.append('../../../../common/schema/' + settings.SCHEMA_VERSION)
from objects import schema as objectSchema
import features
from features import sherlock
#from features.FeatureGroup import FeatureGroup

alert = {
    'ebv': 0.0,
    'diaSourcesList': [
        {
            'psfFlux':100000,    # mag is 18.9
            'midpointMjdTai': 60000,
            'band': 'g',
        },
    ],
    'annotations': {
        'sherlock': [ { } ],
    }
}

class FeatureTest(TestCase):
    def test0_sherlock(self):
        alert['annotations']['sherlock'][0] = {
            'classification': 'SN',
            'direct_distance' : 100  # 100 Mpc
        }
        groupModule = features.sherlock
        groupClass = groupModule.sherlock
        groupInst = groupClass(alert, verbose=True)
        ret = groupInst.run()
        self.assertAlmostEqual(ret['absMag'], -16.1, places=4)

    def test1_sherlock(self):
        alert['annotations']['sherlock'][0] = {
            'classification': 'SN',
            'z'             : 0.1
        }
        groupModule = features.sherlock
        groupClass = groupModule.sherlock
        groupInst = groupClass(alert, verbose=True)
        ret = groupInst.run()
        self.assertAlmostEqual(ret['absMag'], -19.518675881388, places=4)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
