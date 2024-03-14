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
        self.assertIsInstance(result[0], MOC)


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
