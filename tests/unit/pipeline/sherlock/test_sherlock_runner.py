"""Unit tests for sherlock runner
"""

import unittest
import unittest.mock
from unittest.mock import patch
import context
import sherlock_runner


class RunnerTest(unittest.TestCase):

    @patch('sherlock_runner.wrapper')
    @patch('sherlock_runner.lasairLogging')
    def test_run_wrapper(self, mock_logging, mock_wrapper):
        """Test that run works"""
        sherlock_runner.setup_proc(1, 1, '')
        mock_wrapper.run.assert_called_once()
        mock_logging.getLogger.return_value.info.assert_called_with('Ingested 3 alerts')

    @patch('sherlock_runner.wrapper')
    @patch('sherlock_runner.lasairLogging')
    def test_run_wrapper_exception(self, mock_logging, mock_wrapper):
        """Test handling of exception on run"""
        mock_wrapper.run.side_effect = Exception('Test error')
        sherlock_runner.setup_proc(1, 1, '')
        mock_logging.getLogger.return_value.exception.assert_called()
        mock_logging.getLogger.return_value.critical.assert_called_with('Unrecoverable error in filter batch: Test error')


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
