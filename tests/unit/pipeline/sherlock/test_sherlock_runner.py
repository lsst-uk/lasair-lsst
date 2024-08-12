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
        sherlock_runner.setup_proc(None, [], 1, 2, 'test_config.json')
        mock_wrapper.run.assert_called_once()
        mock_logging.getLogger.return_value.info.assert_called_with('Starting sherlock runner process 1 of 2')

    @patch('sherlock_runner.wrapper')
    @patch('sherlock_runner.lasairLogging')
    @patch('sherlock_runner.os.kill')
    def test_run_wrapper_exception(self, mock_kill, mock_logging, mock_wrapper):
        """Test handling of exception on run"""
        mock_exit_code = unittest.mock.MagicMock()
        mock_wrapper.run.side_effect = Exception('Test error')
        # pid needs to be anything except ours
        pid = os.getpid() + 1
        # Check that exit code is set when an exception happens
        sherlock_runner.setup_proc(mock_exit_code, [pid], 1, 1, 'test_config.json')
        # check that the exit code was not 0
        self.assertNotEqual(mock_exit_code.value, 0)
        # check the exception got logged
        mock_logging.getLogger.return_value.exception.assert_called()
        mock_logging.getLogger.return_value.critical.assert_called_with('Unrecoverable error in sherlock: Test error')
        # check SIGTERM got sent
        mock_kill.assert_called()


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
