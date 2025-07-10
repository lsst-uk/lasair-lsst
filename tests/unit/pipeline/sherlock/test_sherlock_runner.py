"""Unit tests for sherlock runner
"""

import os
import sys
import unittest
import unittest.mock
from unittest.mock import patch
import context
import sherlock_runner


def mock_setup_proc(exit_code, pids, n, nprocess, conffile):
    """A mock version of setup proc. Writes arguments to a temporary file that we can check in the test."""
    filename = f"runner_test_output_{ n }_{ nprocess }"
    with open(filename, 'w') as f:
        f.write(f"{ exit_code },{ pids },{ n },{ nprocess },{ conffile }")
        f.close()


class RunnerTest(unittest.TestCase):

    @patch('sherlock_runner.wrapper')
    @patch('sherlock_runner.lasairLogging')
    def test_run_wrapper(self, mock_logging, mock_wrapper):
        """Test that run works"""
        sherlock_runner.setup_proc(None, [], 1, 2, 'test_config.json')
        mock_wrapper.run.assert_called_once()
        mock_logging.getLogger.return_value.info.assert_called_with('Starting sherlock runner process 1 of 2')

    @patch('sherlock_runner.setup_proc', new=mock_setup_proc)
    # @patch('sherlock_runner.Process')
    def test_main(self):
        """Test that main works"""
        testargs = ['sherlock_runner.py', '--nprocess=4']
        with unittest.mock.patch.object(sys, 'argv', testargs):
            # run main() - return value should be 0
            self.assertEqual(0, sherlock_runner.main())
        # test that mock_set_proc created some temporary files and they look reasonable
        for i in range(1, 5):
            filename = f"runner_test_output_{ i }_4"
            with open(filename, 'r') as f:
                (exit_code, pids, n, nprocess, conffile) = f.read().split(',')
                self.assertEqual(str(n), str(i))


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
