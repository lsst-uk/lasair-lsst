import unittest, unittest.mock
from unittest.mock import patch

import subprocess
import context
import filter
import re


class FilterTest(unittest.TestCase):

    # check that the sigterm handler sets sigterm raised correctly
    def test_sigterm_handler(self):
        fltr = filter.Filter(group_id='filter_test', maxalert=0)
        self.assertFalse(fltr.sigterm_raised)
        subprocess.run(['pkill', '-f', 'python3 test_filter.py'])
        self.assertTrue(fltr.sigterm_raised)

    def test_insert_sherlock(self):
        test_ann = {
            "classification": "VS",
            "description": "This is a description",
            "diaObjectId": "ZTF18aaujzlh",
            "catalogue_object_id": "1237655465380610133",
            "raDeg": 191.5944036793479,
            "decDeg": 62.93254720807615,
            "distance": None,
            "unexpected_attribute": "should not appear in output"
        }
        expected_results = [
            "classification='VS'",
            "diaObjectId='ZTF18aaujzlh'",
            "association_type='0'",
            "catalogue_table_name='0'",
            "catalogue_object_id='1237655465380610133'",
            "catalogue_object_type='0'",
            "raDeg='191.5944036793479'",
            "decDeg='62.93254720807615'",
            "separationArcsec='0'",
            "northSeparationArcsec='0'",
            "eastSeparationArcsec='0'",
            "physical_separation_kpc='0'",
            "direct_distance='0'",
            "distance='0'",
            "z='0'",
            "photoZ='0'",
            "photoZErr='0'",
            "Mag='0'",
            "MagFilter='0'",
            "MagErr='0'",
            "classificationReliability='0'",
            "major_axis_arcsec='0'",
            "annotator='0'",
            "additional_output='0'",
            "description='This is a description'",
            "summary='0'"
            ]
        result = filter.Filter.create_insert_sherlock(test_ann)
        result = re.sub("\n",'', result)

        # check that query starts OK
        self.assertRegex(result, "^REPLACE INTO sherlock_classifications SET ")

        # check that the items in the constructed query match the set of expected items
        result = re.sub("^REPLACE INTO sherlock_classifications SET ", "", result)
        self.assertEqual(len(result.split(',')), len(expected_results))
        for item in result.split(','):
            self.assertIn(item, expected_results)

    @patch('filter.FeatureGroup')
    def test_insert_query(self, mock_FeatureGroup):
        mock_FeatureGroup.run_all.return_value = {
            "strFeature": "A string", "floatFeature": 0.123, "nanFeature": float("nan"), "missingFeature": None}
        expected_results = [
            'strFeature="A string"', 'floatFeature=0.123', 'nanFeature=NULL', 'missingFeature=NULL']
        result = filter.Filter.create_insert_query({})
        result = re.sub("\n",'', result)

        # check that query starts OK
        self.assertRegex(result, "^REPLACE INTO objects SET ")

        # check that the items in the constructed query match the set of expected items
        result = re.sub("^REPLACE INTO objects SET ", "", result)
        self.assertEqual(len(result.split(',')), len(expected_results))
        for item in result.split(','):
            self.assertIn(item, expected_results)


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
