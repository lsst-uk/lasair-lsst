"""Unit tests for ingest runner
"""

import os
import unittest
import unittest.mock
from unittest.mock import patch
import context
import ingest_runner
import ingest


class RunnerTest(unittest.TestCase):

    @patch('ingest.Ingester')
    @patch('ingest_runner.lasairLogging')
    def test_run_ingest(self, mock_logging, mock_ingester):
        """Test that run_ingest works"""
        mock_ingester.return_value.run.return_value = 3
        ingest_runner.setup_proc(None, [], 1, 1, {})
        mock_logging.getLogger.return_value.debug.assert_called_with('Ingested 3 alerts')

    @patch('ingest.Ingester')
    @patch('ingest_runner.lasairLogging')
    @patch('ingest_runner.os.kill')
    def test_run_ingest_exception(self, mock_kill, mock_logging, mock_ingester):
        """Test handling of exception on run"""
        mock_exit_code = unittest.mock.MagicMock()
        mock_ingester.return_value.run.return_value = 3
        mock_ingester.return_value.run.side_effect = Exception('Test error')
        # pid needs to be anything except ours
        pid = os.getpid() + 1
        # Check that exit code is set when an exception happens
        ingest_runner.setup_proc(mock_exit_code, [pid], 1, 1, {})
        # check that the exit code was not 0
        self.assertNotEqual(mock_exit_code.value, 0)
        # check the exception got logged
        mock_logging.getLogger.return_value.exception.assert_called()
        mock_logging.getLogger.return_value.critical.assert_called_with('Unrecoverable error in ingest: Test error')
        # check SIGTERM got sent
        mock_kill.assert_called()


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
