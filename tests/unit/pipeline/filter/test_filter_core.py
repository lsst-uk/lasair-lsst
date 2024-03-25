import unittest, unittest.mock
from unittest.mock import patch

import subprocess
import context
from filtercore import Filter
import re


class FilterTest(unittest.TestCase):

    def test_sigterm_handler(self):
        """Test that the sigterm handler sets sigterm raised correctly"""
        fltr = Filter(group_id='filter_test', maxalert=0)
        self.assertFalse(fltr.sigterm_raised)
        subprocess.run(['pkill', '-f', 'python3 test_filter_core.py'])
        self.assertTrue(fltr.sigterm_raised)

    def test_insert_sherlock(self):
        """Test that the method for constructing the sherlock classification insert query from a sherlock annotation
        gives the expected output."""
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
            "association_type=NULL",
            "catalogue_table_name=NULL",
            "catalogue_object_id='1237655465380610133'",
            "catalogue_object_type=NULL",
            "raDeg='191.5944036793479'",
            "decDeg='62.93254720807615'",
            "separationArcsec=NULL",
            "northSeparationArcsec=NULL",
            "eastSeparationArcsec=NULL",
            "physical_separation_kpc=NULL",
            "direct_distance=NULL",
            "distance=NULL",
            "z=NULL",
            "photoZ=NULL",
            "photoZErr=NULL",
            "Mag=NULL",
            "MagFilter=NULL",
            "MagErr=NULL",
            "classificationReliability=NULL",
            "major_axis_arcsec=NULL",
            "annotator=NULL",
            "additional_output=NULL",
            "description='This is a description'",
            "summary=NULL"
            ]
        result = Filter.create_insert_sherlock(test_ann)
        result = re.sub("\n",'', result)

        # check that query starts OK
        self.assertRegex(result, "^REPLACE INTO sherlock_classifications SET ")

        # check that the items in the constructed query match the set of expected items
        result = re.sub("^REPLACE INTO sherlock_classifications SET ", "", result)
        self.assertEqual(len(result.split(',')), len(expected_results))
        for item in result.split(','):
            self.assertIn(item, expected_results)

    @patch('filtercore.FeatureGroup')
    def test_insert_query(self, mock_FeatureGroup):
        """Test that the method for constructing the object table insert gives the expected output given a dict of
        features."""
        mock_FeatureGroup.run_all.return_value = {
            "strFeature": "A string", "floatFeature": 0.123, "nanFeature": float("nan"), "missingFeature": None}
        expected_results = [
            'strFeature="A string"', 'floatFeature=0.123', 'nanFeature=NULL', 'missingFeature=NULL']
        result = Filter.create_insert_query({})
        result = re.sub("\n",'', result)

        # check that query starts OK
        self.assertRegex(result, "^REPLACE INTO objects SET ")

        # check that the items in the constructed query match the set of expected items
        result = re.sub("^REPLACE INTO objects SET ", "", result)
        self.assertEqual(len(result.split(',')), len(expected_results))
        for item in result.split(','):
            self.assertIn(item, expected_results)

    def test_handle_alert_no_sources(self):
        """Test that the handle_alert method returns 0 for an alert with no sources."""
        test_alert = {'diaObject': {'diaObjectId': 'blah'},
                      'diaSourcesList': []}
        fltr = Filter(group_id='filter_test', maxalert=0)
        result = fltr.handle_alert(test_alert)
        self.assertEqual(result, 0)

    @patch('filtercore.Filter.create_insert_query')
    @patch('filtercore.Filter.execute_query')
    def test_handle_alert(self, mock_execute_query, mock_create_insert_query):
        """Test that handle_alert method returns 1 for an alert with sources."""
        mock_create_insert_query.return_value = "QUERY"
        test_alert = {'diaObject': {'diaObjectId': 'blah'},
                      'diaSourcesList': ['']}
        fltr = Filter(group_id='filter_test', maxalert=0)
        result = fltr.handle_alert(test_alert)
        self.assertEqual(result, 1)
        mock_create_insert_query.assert_called_once()
        mock_execute_query.assert_called_once()

    @patch('filtercore.Filter.create_insert_sherlock')
    @patch('filtercore.Filter.create_insert_query')
    @patch('filtercore.Filter.execute_query')
    def test_handle_alert_sherlock(self, mock_execute_query, mock_create_insert_query, mock_create_insert_sherlock):
        """Test that handle_alert method works with a sherlock annotation."""
        mock_create_insert_query.return_value = "QUERY"
        mock_create_insert_sherlock.return_value = "SHERLOCK"
        test_alert = {'diaObject': {'diaObjectId': 'blah'},
                      'diaSourcesList': [''],
                      'annotations': {'sherlock': [{}]}}
        fltr = Filter(group_id='filter_test', maxalert=0)
        result = fltr.handle_alert(test_alert)
        self.assertEqual(result, 1)
        mock_create_insert_query.assert_called_once()
        mock_create_insert_sherlock.assert_called_once()
        mock_execute_query.assert_has_calls(
            [unittest.mock.call("QUERY"), unittest.mock.call("SHERLOCK")], any_order=True)

    @patch('filtercore.manage_status')
    def test_consume_alerts_sigterm(self, mock_manage_status):
        """Test that consume alerts stops when sigterm raised"""
        mock_consumer = unittest.mock.MagicMock()
        mock_consumer.poll.return_value = None
        fltr = Filter(group_id='filter_test', maxalert=1)
        fltr.consumer = mock_consumer
        fltr.sigterm_raised = True
        result = fltr.consume_alerts()
        self.assertEqual(result, 0)
        mock_consumer.poll.assert_not_called()

    @patch('filtercore.manage_status')
    def test_consume_alerts_none(self, mock_manage_status):
        """Test that consume alerts returns 0 when poll returns None"""
        mock_consumer = unittest.mock.MagicMock()
        mock_consumer.poll.return_value = None
        fltr = Filter(group_id='filter_test', maxalert=1)
        fltr.consumer = mock_consumer
        result = fltr.consume_alerts()
        self.assertEqual(result, 0)
        mock_consumer.poll.assert_called_once()

    @patch('filtercore.manage_status')
    def test_consume_alerts_error(self, mock_manage_status):
        """Test consume alerts when poll returns error"""
        mock_consumer = unittest.mock.MagicMock()
        mock_log = unittest.mock.MagicMock()
        mock_consumer.poll.return_value.error.return_value = "test error"
        fltr = Filter(group_id='filter_test', maxalert=1)
        fltr.consumer = mock_consumer
        fltr.log = mock_log
        result = fltr.consume_alerts()
        self.assertEqual(result, 0)
        self.assertEqual(mock_consumer.poll.call_count, 101)

    @patch('filtercore.Filter.handle_alert')
    @patch('filtercore.manage_status.manage_status')
    def test_consume_alerts(self, mock_manage_status, mock_handle_alert):
        """Test consume alerts"""
        mock_consumer = unittest.mock.MagicMock()
        mock_log = unittest.mock.MagicMock()
        mock_consumer.poll.return_value.error.return_value = None
        mock_consumer.poll.return_value.value.return_value = '{"diaObject": {"diaObjectId":123}}'
        mock_handle_alert.return_value = 1
        fltr = Filter(group_id='filter_test', maxalert=1)
        fltr.consumer = mock_consumer
        fltr.log = mock_log
        result = fltr.consume_alerts()
        self.assertEqual(result, 1)
        mock_consumer.poll.assert_called_once()
        mock_manage_status.assert_called_once()
        mock_manage_status.return_value.add.assert_called_once()

    @patch('filtercore.Filter.execute_query')
    def test_tansfer_to_main_local_error(self, mock_execute_query):
        """Test that an error when building the CSV causes transfer_to_main to return None"""
        mock_log = unittest.mock.MagicMock()
        mock_execute_query.side_effect = Exception('test error')
        fltr = Filter(group_id='filter_test', maxalert=0)
        fltr.log = mock_log
        result = fltr.transfer_to_main()
        self.assertEqual(result, False)
        mock_log.error.assert_called_once()

    @patch('filtercore.Filter.execute_query')
    @patch('filtercore.db_connect.remote')
    def test_tansfer_to_main_remote_connect_error(self, mock_db_connect_remote, mock_execute_query):
        """Test that an error connecting to main db causes transfer_to_main to return None"""
        mock_log = unittest.mock.MagicMock()
        mock_db_connect_remote.side_effect = Exception('test error')
        fltr = Filter(group_id='filter_test', maxalert=0)
        fltr.log = mock_log
        result = fltr.transfer_to_main()
        self.assertEqual(result, False)
        self.assertEqual(mock_execute_query.call_count, 4)
        mock_log.error.assert_called_once()
        mock_db_connect_remote.assert_called_once()

    # @patch('filtercore.Filter.execute_query')
    # @patch('filtercore.db_connect.remote')
    # @patch('os.system')
    # def test_tansfer_to_main_remote_cli_error(self, mock_system, mock_db_connect_remote, mock_execute_query):
    #     """Test that an error writing to main db using the cli causes transfer_to_main to return None"""
    #     mock_log = unittest.mock.MagicMock()
    #    mock_system.return_value = 1
    #    fltr = Filter(group_id='filter_test', maxalert=0)
    #    fltr.log = mock_log
    #    result = fltr.transfer_to_main()
    #    self.assertEqual(result, False)
    #    mock_log.error.assert_called()

    @patch('filtercore.Filter.execute_query')
    @patch('filtercore.db_connect.remote')
    def test_tansfer_to_main_remote_write_error(self, mock_db_connect_remote, mock_execute_query):
        """Test that an error writing to main db causes transfer_to_main to return False"""
        mock_log = unittest.mock.MagicMock()
        mock_cursor = unittest.mock.MagicMock()
        mock_cursor.execute.side_effect = Exception('test error')
        mock_db_connect_remote.return_value.cursor.return_value = mock_cursor
        fltr = Filter(group_id='filter_test', maxalert=0)
        fltr.log = mock_log
        result = fltr.transfer_to_main()
        self.assertEqual(result, False)
        mock_log.error.assert_called()

    # @patch('filtercore.Filter.execute_query')
    # @patch('filtercore.db_connect.remote')
    # @patch('os.system')
    # def test_tansfer_to_main_cli_normal_flow(self, mock_system, mock_db_connect_remote, mock_execute_query):
    #     """Test transfer to main normal flow using the cli"""
    #     mock_log = unittest.mock.MagicMock()
    #     mock_system.return_value = 0
    #     mock_consumer = unittest.mock.MagicMock()
    #     fltr = Filter(group_id='filter_test', maxalert=0)
    #     fltr.log = mock_log
    #     fltr.consumer = mock_consumer
    #     result = fltr.transfer_to_main()
    #     self.assertEqual(result, True)

    @patch('filtercore.Filter.execute_query')
    @patch('filtercore.db_connect.remote')
    def test_tansfer_to_main(self, mock_db_connect_remote, mock_execute_query):
        """Test transfer to main normal flow"""
        mock_log = unittest.mock.MagicMock()
        mock_consumer = unittest.mock.MagicMock()
        mock_cursor = unittest.mock.MagicMock()
        mock_db_connect_remote.return_value.cursor.return_value = mock_cursor
        fltr = Filter(group_id='filter_test', maxalert=0)
        fltr.log = mock_log
        fltr.consumer = mock_consumer
        result = fltr.transfer_to_main()
        self.assertEqual(result, True)
        mock_log.error.assert_not_called()
        self.assertEqual(mock_cursor.execute.call_count, 4)
        mock_consumer.commit.assert_called_once()


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
