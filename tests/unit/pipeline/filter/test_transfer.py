"""Unit tests for filter runner
"""

import unittest
import unittest.mock
from unittest.mock import MagicMock, patch
import context
import transfer


class TransferTest(unittest.TestCase):

    def test_fetch_attrs(self):
        """Test getting a list of column names"""
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter([{'column_name': 'col_one'},{'column_name': 'col_two'}])
        mock_msl = MagicMock()
        mock_msl.cursor.return_value = mock_cursor
        result = transfer.fetch_attrs(mock_msl, 'my_table')
        self.assertEqual(result, ['col_one', 'col_two'])

    def test_fetch_attrs_error(self):
        """Test that an error on getting a list of column names returns false and logs an error"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception('test exception')
        mock_msl = MagicMock()
        mock_msl.cursor.return_value = mock_cursor
        mock_log = MagicMock()
        result = transfer.fetch_attrs(mock_msl, 'my_table', log=mock_log)
        self.assertFalse(result)
        mock_log.error.assert_called()

    def test_transfer(self):
        """Test transfer csv (doesn't actually do very much)"""
        result = transfer.transfer_csv(
            MagicMock(name='msl_local'),
            MagicMock(name='msl_remote'),
            ['attr', 'list'],
            'table_from',
            'table_to')
        self.assertTrue(result)

    def test_transfer_error(self):
        """Test that an error on transfer csv returns false and logs an error"""
        mock_log = MagicMock()
        mock_msl_local = MagicMock()
        mock_msl_local.cursor.return_value.execute.side_effect = Exception('test exception')
        result = transfer.transfer_csv(
            mock_msl_local,
            MagicMock(name='msl_remote'),
            ['attr', 'list'],
            'table_from',
            'table_to',
            log=mock_log)
        self.assertFalse(result)
        mock_log.error.assert_called()

    @patch('db_connect.remote')
    @patch('db_connect.local')
    @patch('os.system')
    @patch('transfer.transfer_csv')
    def test_main(self, mock_transfer, mock_system, mock_local, mock_remote):
        """Test that main runs and calls transfer_csv."""
        transfer.main()
        mock_transfer.assert_called()


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
