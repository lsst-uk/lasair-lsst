"""
Test that for every feature defined in the features schema,
an iplementation exists.
"""
import sys
import importlib
import unittest.main
from unittest import TestCase
import context
sys.path.append('../../../../pipeline/filter/features')
sys.path.append('../../../../common/schema/lasair_schema')
#from diaObjects import schema as objectSchema
from testObjects import schema as objectSchema
import json

class FeatureTest(TestCase):
  def test1_import_features(cls):
    """For every feature defined in the schema, try to import the implementation."""
    for feature in objectSchema['fields']:
      name = feature['name']
      featureModule = importlib.import_module(name)

  def test2_get_schema(self):
    """Check that for every feature we can get the schema."""
    for feature in objectSchema['fields']:
      name = feature['name']
      featureModule = importlib.import_module(name)
      featureClass = getattr(featureModule, name)
      schema = featureClass.get_schema()
      # check that returned schema is a dict
      self.assertTrue(isinstance(schema, dict))
      # check that schema contains a "type" element
      self.assertIn("type", schema)

  def test3_get_info(self):
    """Check that we get a documentation string back."""
    for feature in objectSchema['fields']:
      name = feature['name']
      featureModule = importlib.import_module(name)
      featureClass = getattr(featureModule, name)
      info = featureClass.get_info()
      # check that the info string is a string
      self.assertTrue(isinstance(info, str))

  def test4_run_feature(self):
    """Check that the feature runs"""
    with open("sample_alerts/1g1r.json") as f:
      alert = json.load(f)
      for feature in objectSchema['fields']:
        name = feature['name']
        featureModule = importlib.import_module(name)
        featureClass = getattr(featureModule, name)
        result = featureClass.run(alert)
        # check that the result is a dict
        #self.assertTrue(isinstance(result, dict))
        # check that the result is the type specified in the schema
        self.assertTrue(isinstance(result, eval(feature['type'])))

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()



