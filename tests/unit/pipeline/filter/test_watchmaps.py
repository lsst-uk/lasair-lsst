"""Unit tests for the watchmaps module
"""

import unittest, unittest.mock
from unittest.mock import patch
from mocpy import MOC

import context
import watchmaps


class WatchmapsTest(unittest.TestCase):

    def test_read_cache_files_dir_error(self):
        """Test that calling read_watchmap_cache_files on a non-existant directory returns None
        """
        mock_fltr = unittest.mock.MagicMock()
        result = watchmaps.read_watchmap_cache_files(mock_fltr, "/tmp/this_directory_should_not_exist_qnfggib3")
        self.assertIsNone(result)
        mock_fltr.log.error.assert_called_once()

    def test_read_cache_files(self):
        """Test calling read_watchmap_cache_files normal flow
        """
        mock_fltr = unittest.mock.MagicMock()
        result = watchmaps.read_watchmap_cache_files(mock_fltr, "./sample_areas")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['ar_id'], 1)
        self.assertIsInstance(result[0]['moc'], MOC)

    def test_check_alerts_against_watchmap_error(self):
        """Test check_alerts_against_watchmap returns empty list on error
        """
        test_alertlist = {"obj": ['ABC123'], "ra": [0.123], "de": [0.456]}
        mock_fltr = unittest.mock.MagicMock()
        mock_moc = unittest.mock.MagicMock()
        test_watchmap = {'ar_id': 1, 'moc': mock_moc}
        mock_moc.contains.side_effect = Exception("test error")
        result = watchmaps.check_alerts_against_watchmap(mock_fltr, test_alertlist, test_watchmap)
        self.assertEqual(len(result), 0)
        mock_fltr.log.error.assert_called_once()

    def test_check_alerts_against_watchmap(self):
        """Test check_alerts_against_watchmap normal flow
        """
        test_alertlist = {
            "obj": ['ABC123', 'DEF456'],
            "ra": [0.123, 4.567],
            "de": [0.456, -8.90]
        }
        mock_fltr = unittest.mock.MagicMock()
        mock_watchmap = {'ar_id': 1, 'moc': unittest.mock.MagicMock()}
        result = watchmaps.check_alerts_against_watchmap(mock_fltr, test_alertlist, mock_watchmap)
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
