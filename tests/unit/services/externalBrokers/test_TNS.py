import context
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../services/externalBrokers/TNS')))
import fetch_from_tns
import poll_tns
import tns_crossmatch
import tns_runner
import unittest


class TNSTest(unittest.TestCase):
    """Placeholder"""


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    