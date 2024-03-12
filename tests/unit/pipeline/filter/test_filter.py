import unittest, unittest.mock
from unittest.mock import patch

import subprocess
import context
import filter


class FilterTest(unittest.TestCase):

    # check that the sigterm handler sets sigterm raised correctly
    def test_sigterm_handler(self):
        fltr = filter.Filter(group_id='filter_test', maxalert=0)
        self.assertFalse(fltr.sigterm_raised)
        subprocess.run(['pkill', '-f', 'python3 test_filter.py'])
        self.assertTrue(fltr.sigterm_raised)
        

if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
