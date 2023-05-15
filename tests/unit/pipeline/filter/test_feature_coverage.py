"""
Test that for every feature defined in the features schema,
an iplementation exists.
"""
import sys
import unittest.main
from unittest import TestCase
import context
sys.path.append('../../../../pipeline/filter/features')

class FeatureCoverageTest(TestCase):
  def test_feature_coverage(self):
    from schema_features import schema 
    for feature in schema['fields']:
      exec(f"import {feature['name']}")

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()



