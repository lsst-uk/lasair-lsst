import sys
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
from features import *
from modify_alert import modify

sample = 'Tidal_disruption_event_TDE_114933870'

class FeatureTest(TestCase):
  def test0_get_features(self):
    """Check that for every feature in the schema an implementing class exists."""
    impl_features = set()
    for group in features.__all__:
      groupModule = getattr(features, group)
      groupClass = getattr(groupModule, group)
      impl_features.update(groupClass.get_features())
    for feature in objectSchema['fields']:
      if 'name' in feature and feature['origin'] != 'external':
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
    with open("sample_alerts/%s.json"%sample) as f_in, open("sample_alerts/%s_object.json"%sample) as f_out:
      sample_alert = modify(json.load(f_in))
      sample_output = json.load(f_out)
      output = {}
      schema = {}
      for group in features.__all__:
        groupModule = getattr(features, group)
        groupClass = getattr(groupModule, group)
        schema.update(groupClass.get_schema())
        groupInst = groupClass(sample_alert, verbose=True)
        output.update(groupInst.run())
        #print(groupInst.run())
      # check the output exists
      self.assertTrue(isinstance(schema, dict))
      self.assertTrue(isinstance(output, dict))
      # check the output matches the schema
      for feature in schema:
        name = schema[feature]['name']
        type = schema[feature]['type']
        # check name is in the feature set
        self.assertIn(name, output)
        # check that either the type is ok or that the output is None and allowed to be so 
        self.assertTrue(
          (isinstance(output[name], eval(type))) or
          (output[name] is None and schema[feature].get('extra') != 'NOT NULL')
          )
        # check that the content is correct
        if isinstance(output[name], float):
          self.assertAlmostEqual(output[name], sample_output[name], places=4, msg=name)
        else:
          self.assertEqual(output[name], sample_output[name], msg=name)

  def test4_run_all(self):
    """Test the run_all method"""
    from features.FeatureGroup import FeatureGroup
    with open("sample_alerts/%s.json"%sample) as f:
      alert = modify(json.load(f))
      output = FeatureGroup.run_all(alert, verbose=True)
      self.assertTrue(isinstance(output, dict))

  def test5_run_all(self):
    """Test the lightcurve_lite method"""
    from filters import lightcurve_lite
    with open("sample_alerts/%s.json"%sample) as f_in, open("sample_alerts/%s_lite.json"%sample) as f_out:
      alert = modify(json.load(f_in))
      output = lightcurve_lite(alert)
      sample_output = json.load(f_out)
      self.assertEqual(output, sample_output)

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()
