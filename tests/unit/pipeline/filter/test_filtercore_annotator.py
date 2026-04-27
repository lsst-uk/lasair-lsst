import unittest, unittest.mock
from unittest.mock import patch

import psutil
import context
from annotationcore import AnnotationFilter
import ann_filters
import re

def test_message_handler(message_list):
    return len(message_list)

class FilterTest(unittest.TestCase):

    def test_sigterm_handler(self):
        """Test that the sigterm handler sets sigterm raised correctly"""
        fltr = AnnotationFilter(group_id='filter_test', maxmessage=0)
        self.assertFalse(fltr.sigterm_raised)
        psutil.Process().terminate()
        self.assertTrue(fltr.sigterm_raised)

#    def test_insert_query(self, mock_FeatureGroup):
#        """Test that the method for constructing the object table insert gives the expected output given a dict of
#        features."""
#        mock_FeatureGroup.run_all.return_value = {
#            "strFeature": "A string", "floatFeature": 0.123, "nanFeature": float("nan"), "missingFeature": None}
#        expected_results = [
#            'strFeature="A string"', 'floatFeature=0.123', 'nanFeature=NULL', 'missingFeature=NULL']
#        result = AnnotationFilter.create_insert_query({})
#        result = re.sub("\n",'', result)
#
#        # check that query starts OK
#        self.assertRegex(result, "^REPLACE INTO objects SET ")
#
#        # check that the items in the constructed query match the set of expected items
#        result = re.sub("^REPLACE INTO objects SET ", "", result)
#        self.assertEqual(len(result.split(',')), len(expected_results))
#        for item in result.split(','):
#            self.assertIn(item, expected_results)

    @patch('filtercore.Filter.execute_remote_query')
    def test_ingest_annotation(self, mock_execute_remote_query):
        """Test that handle_annotation method returns 1 for an annotation with sources."""
        test_annotation = {'diaObjectId': 123, 
                 'topic':'test_topic', 
                 'version': '0.1',
                 'classification':'fruit',
                 'explanation': 'fruity',
                 'classdict':{'apple':0.9, 'pear': 0.1},
                 'url': '',
                }
        fltr = AnnotationFilter(group_id='filter_test', maxmessage=0)
        fltr.ann_diaObjectId = {}
        result = fltr.ingest_annotation(test_annotation)
        self.assertEqual(result, 1)
        mock_execute_remote_query.assert_called_once()

    @patch('annotationcore.AnnotationFilter.ingest_annotation')
    @patch('annotationcore.AnnotationFilter.ingest_message_list')
    def test_consume_annotations(self, mock_ingest_annotation, mock_ingest_message_list):
        """Test consume annotations"""
        mock_consumer      = unittest.mock.MagicMock()
        mock_log           = unittest.mock.MagicMock()
        mock_sfd           = unittest.mock.MagicMock()
        mock_manage_status = unittest.mock.MagicMock()
        mock_sfd.return_value = [0]
        mock_consumer.poll.return_value.error.return_value = None
        mock_consumer.poll.return_value.value.return_value = '{"diaObject": {"diaObjectId":123, "ra":23, "decl":23}}'
#        mock_ingest_annotation.return_value = 1
        fltr = AnnotationFilter(group_id='filter_test', maxmessage=1)
        fltr.ms       = mock_manage_status
        fltr.consumer = mock_consumer
        fltr.log      = mock_log
        fltr.sfd      = mock_sfd
        fltr.nid      = 0
        result = fltr.consume_messages(test_message_handler)
        self.assertEqual(result, 1)
        mock_consumer.poll.assert_called_once()
        mock_manage_status.add.assert_called_once()

    def test_append_lightcurve(self):
        mock_fltr = unittest.mock.MagicMock()
        def fetch_side_effect(diaObjectId, lite=False):
            return (f"obj_{diaObjectId}", [f"src_{diaObjectId}"], [f"forced_{diaObjectId}"])
        mock_fltr.lightcurve = unittest.mock.MagicMock()
        mock_fltr.lightcurve.fetch.side_effect = fetch_side_effect
        mock_fltr.message_dict = {}

        query_results = [
            {'diaObjectId': 1234},
            {'diaObjectId': 5678}
        ]

        ann_filters.append_lightcurve(mock_fltr, query_results)

        self.assertEqual(len(mock_fltr.message_dict), 2)
        self.assertEqual(mock_fltr.message_dict[1234]['diaObject'], "obj_1234")
        self.assertEqual(mock_fltr.message_dict[1234]['diaSourcesList'], ["src_1234"])
        self.assertEqual(mock_fltr.message_dict[1234]['diaForcedSourcesList'], ["forced_1234"])
        self.assertEqual(mock_fltr.message_dict[5678]['diaObject'], "obj_5678")
        self.assertEqual(mock_fltr.message_dict[5678]['diaSourcesList'], ["src_5678"])
        self.assertEqual(mock_fltr.message_dict[5678]['diaForcedSourcesList'], ["forced_5678"])
        self.assertEqual(mock_fltr.lightcurve.fetch.call_count, 2)
        mock_fltr.lightcurve.fetch.assert_any_call(1234, lite=False)
        mock_fltr.lightcurve.fetch.assert_any_call(5678, lite=False)

    def test_append_lightcurve_empty_input(self):
        """Verify the function handles an empty results list without error."""
        mock_fltr = unittest.mock.MagicMock()
        mock_fltr.lightcurve = unittest.mock.MagicMock()
        mock_fltr.message_dict = {}
        ann_filters.append_lightcurve(mock_fltr, [])
        self.assertEqual(len(mock_fltr.message_dict), 0)
        mock_fltr.lightcurve.fetch.assert_not_called()

if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
