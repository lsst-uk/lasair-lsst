"""Unit tests for the watchlists module
"""

import unittest, unittest.mock
from unittest.mock import patch

import context
import watchlists


class WatchlistsTest(unittest.TestCase):

    def test_insert_watchlist_hits(self):
        """Test insert_watchlist_hits method normal flow
        """
        test_hits = [
            {
                'wl_id': 1,
                'cone_id': 2,
                'diaObjectId': 'ABC123',
                'arcsec': 0.5,
                'name': 'foo',
            }
        ]
        mock_fltr = unittest.mock.MagicMock()
        watchlists.insert_watchlist_hits(mock_fltr, test_hits)
        mock_fltr.execute_query.assert_called_with(
            'REPLACE into watchlist_hits (wl_id, cone_id, diaObjectId, arcsec, name) VALUES\n'
            '(1,2,"ABC123",0.500,"foo")'
        )

    def test_insert_watchlist_hits_error(self):
        """Test insert_watchlist_hits method on database error
        """
        test_hits = [
            {
                'wl_id': 1,
                'cone_id': 2,
                'diaObjectId': 'ABC123',
                'arcsec': 0.5,
                'name': 'foo',
            }
        ]
        mock_fltr = unittest.mock.MagicMock()
        mock_fltr.execute_query.side_effect = Exception("test error")
        watchlists.insert_watchlist_hits(mock_fltr, test_hits)
        mock_fltr.log.error.assert_called_once()

    def test_read_cache_files_dir_error(self):
        """Test that calling read_watchlist_cache_files on a non-existant directory returns None
        """
        mock_fltr = unittest.mock.MagicMock()
        result = watchlists.read_watchlist_cache_files(mock_fltr, "/tmp/this_directory_should_not_exist_sndgeii7")
        self.assertIsNone(result)
        mock_fltr.log.error.assert_called_once()


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
