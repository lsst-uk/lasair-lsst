import sys
import context
import unittest.main
from unittest import TestCase
import json
sys.path.append('../../../../pipeline/filter')
sys.path.append('../../../../common/schema/lasair_schema')
sys.path.append('../../../../pipeline/filter/features')
from objects import schema as objectSchema
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
        if 'name' in feature:
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
#    with open("sample_alerts/402778310355976216.json") as f:
    with open("sample_alerts/99999999999.json") as f:
      alert = json.load(f)
      output = {}
      schema = {}
      for group in features.__all__:
        groupModule = getattr(features, group)
        groupClass = getattr(groupModule, group)
        schema.update(groupClass.get_schema())
        groupInst = groupClass(alert, verbose=True)
        output.update(groupInst.run())
        #print(groupInst.run())
      # check the output exists
      self.assertTrue(isinstance(schema, dict))
      self.assertTrue(isinstance(output, dict))
      # check the output matches the schema
      for feature in schema:
        if not 'name' in feature:
            continue
        name = schema[feature]['name']
        if name == 'timestamp':
            continue
        type = schema[feature]['type']
        if type == 'string':
            type = 'str'
        # check name is in the feature set
        self.assertIn(name, output)
        # check that either the type is ok or that the output is None and allowed to be so 
        print('===', name, type, output[name])
        self.assertTrue(
          (isinstance(output[name], eval(type))) or
          (output[name] is None and schema[feature].get('extra') != 'NOT NULL')
          )

  def test4_run_all(self):
    """Test the run_all method"""
    from features.FeatureGroup import FeatureGroup
#    with open("sample_alerts/402778310355976216.json") as f:
    with open("sample_alerts/99999999999.json") as f:
      alert = json.load(f)
      output = FeatureGroup.run_all(alert, verbose=True)
      self.assertTrue(isinstance(output, dict))

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()



