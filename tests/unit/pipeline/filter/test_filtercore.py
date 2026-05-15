import unittest, unittest.mock
from unittest.mock import patch

import psutil
import context
from filtercore import Filter
import re


class FilterTest(unittest.TestCase):
    """Tests for filter base class"""

    def test_execute_local_query(self):
        """Test executing a local query."""
        fltr = Filter()
        mock_db = unittest.mock.MagicMock()
        fltr.database_local = mock_db
        fltr.execute_local_query("SELECT * FROM things")
        # cursor should have been called once
        mock_db.cursor.assert_called_once()
        # execute should have been called once
        mock_db.cursor.return_value.execute.assert_called_with("SELECT * FROM things")
        # commit should have been called once
        mock_db.commit.assert_called_once()

    @patch('db_connect.local')
    def test_execute_local_query_disconnected(self, mock_local):
        """Test executing a local query when the db is not connected."""
        mock_log = unittest.mock.MagicMock()
        mock_db = unittest.mock.MagicMock()
        # dbconnect.local should return the mock db when called
        mock_local.return_value = mock_db
        fltr = Filter(log=mock_log)
        mock_db.is_connected.return_value = False
        fltr.database_local = mock_db
        fltr.execute_local_query("SELECT * FROM things")
        # a warning should be logged
        mock_log.warning.assert_called()
        # we should try to reconnect
        mock_local.assert_called()
        # cursor should have been called once
        mock_db.cursor.assert_called_once()
        # execute should have been called once
        mock_db.cursor.return_value.execute.assert_called_with("SELECT * FROM things")
        # commit should have been called once
        mock_db.commit.assert_called_once()

    def test_execute_local_query_error(self):
        """Test getting an error executing a local query."""
        mock_log = unittest.mock.MagicMock()
        fltr = Filter(log=mock_log)
        mock_db = unittest.mock.MagicMock()
        mock_db.cursor.return_value.execute.side_effect = Exception('test')
        fltr.database_local = mock_db
        with self.assertRaises(Exception):
            fltr.execute_local_query("SELECT * FROM things")
            # an error should be logged
            mock_log.error.assert_called()
            # cursor should have been called once
            mock_db.cursor.assert_called_once()
            # execute should have been called once
            mock_db.cursor.return_value.execute.assert_called_with("SELECT * FROM things")
            # commit should NOT have been called once
            mock_db.commit.assert_not_called()

    def test_execute_remote_query(self):
        """Test executing a remote query."""
        fltr = Filter()
        mock_db = unittest.mock.MagicMock()
        fltr.database_remote = mock_db
        fltr.execute_remote_query("SELECT * FROM things")
        # cursor should have been called once
        mock_db.cursor.assert_called_once()
        # execute should have been called once
        mock_db.cursor.return_value.execute.assert_called_with("SELECT * FROM things")
        # commit should have been called once
        mock_db.commit.assert_called_once()

    @patch('db_connect.remote')
    def test_execute_remote_query_disconnected(self, mock_remote):
        """Test executing a remote query when the db is not connected."""
        mock_log = unittest.mock.MagicMock()
        mock_db = unittest.mock.MagicMock()
        # dbconnect.remote should return the mock db when called
        mock_remote.return_value = mock_db
        fltr = Filter(log=mock_log)
        mock_db.is_connected.return_value = False
        fltr.database_remote = mock_db
        fltr.execute_remote_query("SELECT * FROM things")
        # a warning should be logged
        mock_log.warning.assert_called()
        # we should try to reconnect
        mock_remote.assert_called()
        # cursor should have been called once
        mock_db.cursor.assert_called_once()
        # execute should have been called once
        mock_db.cursor.return_value.execute.assert_called_with("SELECT * FROM things")
        # commit should have been called once
        mock_db.commit.assert_called_once()

    def test_execute_remote_query_error(self):
        """Test getting an error executing a remote query."""
        mock_log = unittest.mock.MagicMock()
        fltr = Filter(log=mock_log)
        mock_db = unittest.mock.MagicMock()
        mock_db.cursor.return_value.execute.side_effect = Exception('test')
        fltr.database_remote = mock_db
        with self.assertRaises(Exception):
            fltr.execute_remote_query("SELECT * FROM things")
            # an error should be logged
            mock_log.error.assert_called()
            # cursor should have been called once
            mock_db.cursor.assert_called_once()
            # execute should have been called once
            mock_db.cursor.return_value.execute.assert_called_with("SELECT * FROM things")
            # commit should NOT have been called once
            mock_db.commit.assert_not_called()


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
