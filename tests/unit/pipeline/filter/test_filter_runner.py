"""Unit tests for filter runner
"""

import unittest
import unittest.mock
from unittest.mock import patch
import psutil
import context
import filter_runner


class RunnerTest(unittest.TestCase):

    def test_sigterm_handler(self):
        """Test that the sigterm handler sets sigterm raised correctly"""
        self.assertFalse(filter_runner.stop)
        psutil.Process().terminate()
        self.assertTrue(filter_runner.stop)

    @patch('filter_runner.filtercore.Filter.run_batch')
    def test_batch_with_alerts(self, mock_run_batch):
        """Test that when run_batch returns positive we end the loop after running maxbatch batches"""
        mock_log = unittest.mock.MagicMock()
        mock_run_batch.return_value = 3
        filter_runner.run({'--maxbatch': 2}, mock_log)
        mock_log.info.assert_called_with('Exiting filter runner')
        self.assertEqual(mock_run_batch.call_count, 2)

    @patch('filter_runner.filtercore.Filter.run_batch')
    def test_batch_no_alerts(self, mock_run_batch):
        """Test that when run_batch returns 0 we wait for more alerts"""
        mock_log = unittest.mock.MagicMock()
        mock_run_batch.return_value = 0
        filter_runner.run({'--maxbatch': 1}, mock_log)
        self.assertIn(unittest.mock.call('Waiting for more alerts ....'), mock_log.info.call_args_list)

    @patch('filter_runner.filtercore.Filter.run_batch')
    def test_batch_exception(self, mock_run_batch):
        """Test handling of exception on run"""
        mock_log = unittest.mock.MagicMock()
        mock_run_batch.side_effect = Exception('Test error')
        # Check that sys.exit is called when an exception happens
        with self.assertRaises(SystemExit) as cm:
            filter_runner.run({'--maxbatch': 1}, mock_log)
        # check that the exit code was not 0
        self.assertNotEqual(cm.exception.code, 0)
        # check the exception was the expected one
        mock_log.exception.assert_called()
        # check the exception got logged
        mock_log.critical.assert_called_with('Unrecoverable error in filter batch: Test error')


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
