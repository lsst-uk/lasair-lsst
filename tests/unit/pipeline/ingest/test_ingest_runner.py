"""Unit tests for ingest runner
"""

import unittest
import unittest.mock
from unittest.mock import patch
import psutil
import context
import ingest_runner


class RunnerTest(unittest.TestCase):

    @patch('ingest_runner.ingest.Ingester.run')
    @patch('ingest_runner.lasairLogging')
    def test_run_ingest(self, mock_logging, mock_run):
        """Test that run_ingest works"""
        mock_log = unittest.mock.MagicMock()
        mock_run.return_value = 1
        ingest_runner.setup_proc(1, 1, {'--maxbatch': 2})


    # @patch('filter_runner.filtercore.Filter.run_batch')
    # def test_batch_no_alerts(self, mock_run_batch):
    #     """Test that when run_batch returns 0 we wait for more alerts"""
    #     mock_log = unittest.mock.MagicMock()
    #     mock_run_batch.return_value = 0
    #     filter_runner.run({'--maxalert': 1}, mock_log)
    #     self.assertIn(unittest.mock.call('Waiting for more alerts ....'), mock_log.info.call_args_list)
    #
    # @patch('filter_runner.filtercore.Filter.run_batch')
    # def test_batch_exception(self, mock_run_batch):
    #     """Test that when run_batch returns 0 we wait for more alerts"""
    #     mock_log = unittest.mock.MagicMock()
    #     mock_run_batch.side_effect = Exception('Test error')
    #     filter_runner.run({'--maxbatch': 1}, mock_log)
    #     mock_log.critical.assert_called_with('Unrecoverable error in filter batch: Test error')
    #     mock_log.info.assert_called_with('Exiting filter runner')


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
