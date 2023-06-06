"""
Test that for every feature defined in the features schema,
an iplementation exists.
"""
import sys
import context
import unittest.main
from unittest import TestCase
import json
sys.path.append('../../../../pipeline/filter')
sys.path.append('../../../../common/schema/lasair_schema')
from objects import schema as objectSchema
import features
from features import *

class FeatureTest(TestCase):
  def test1_get_schema(self):
    """Check that for every feature we can get the schema."""
    for feature in objectSchema['fields']:
      name = feature['name']
      featureModule = getattr(features, name)
      featureClass = getattr(featureModule, name)
      schema = featureClass.get_schema()
      # check that returned schema is a dict
      self.assertTrue(isinstance(schema, dict))
      # check that schema contains a "type" element
      self.assertIn("type", schema[name])

  def test2_get_info(self):
    """Check that we get a documentation string back."""
    for feature in objectSchema['fields']:
      name = feature['name']
      featureModule = getattr(features, name)
      featureClass = getattr(featureModule, name)
      info = featureClass.get_info()
      # check that the info string is a string
      self.assertTrue(isinstance(info[name], str))

  def test3_run_feature(self):
    """Check that the feature runs"""
    with open("sample_alerts/lsst1.json") as f:
      alert = json.load(f)
      for feature in objectSchema['fields']:
        name = feature['name']
        featureModule = getattr(features, name)
        featureClass = getattr(featureModule, name)
        schema = featureClass.get_schema()
        result = featureClass(alert).run()
        # check that the result is the type specified in the schema
        self.assertIsInstance(result[name], eval(schema[name]['type']))

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()



