import sys
import context
import unittest.main
from unittest import TestCase
import json
sys.path.append('../../../../pipeline/filter')
sys.path.append('../../../../common/schema/lasair_schema')
#from objects import schema as objectSchema
from testSchema import schema as objectSchema
import features
from features import *

class FeatureTest(TestCase):
  def test0_get_features(self):
    """Check that for every feature in the schema an implementing class exists."""
    impl_features = set()
    for group in features.__all__:
      groupModule = getattr(features, group)
      groupClass = getattr(groupModule, group)
      impl_features.update(groupClass.get_features())
    for feature in objectSchema['fields']:
      name = feature['name']
      self.assertIn(name, impl_features)

  def test1_get_schema(self):
    """Check that for every feature group we can get the schema."""
    for group in features.__all__:
      groupModule = getattr(features, group)
      groupClass = getattr(groupModule, group)
      schema = groupClass.get_schema()
      # check that returned schema is a dict
      self.assertTrue(isinstance(schema, dict))
      # check that each feature contains a "type" element
      for feature in schema:
        self.assertIn("type", schema[feature])

  def test2_get_info(self):
    """Check that we get a documentation dict back."""
    for group in features.__all__:
      groupModule = getattr(features, group)
      groupClass = getattr(groupModule, group)
      info = groupClass.get_info()
      # check that the info is a dict
      self.assertTrue(isinstance(info, dict))
      # check that each feature exists and contains a string
      for feature in groupClass.get_features():
        self.assertIn(feature, info)
        self.assertTrue(info[feature], str)

  def test3_run_feature(self):
    """Check that the feature runs"""
    with open("sample_alerts/lsst1.json") as f:
      alert = json.load(f)
      output = {}
      for group in features.__all__:
        groupModule = getattr(features, group)
        groupClass = getattr(groupModule, group)
        groupInst = groupClass(alert)
        output.update(groupInst.run())
      # check the output exists
      self.assertTrue(isinstance(output, dict))
      # check the output matches the schema
      schema = groupClass.get_schema()
      for feature in schema:
        name = schema[feature]['name']
        type = schema[feature]['type']
        self.assertTrue(isinstance(output[name], eval(type)))

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()



