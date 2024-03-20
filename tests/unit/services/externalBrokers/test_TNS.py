import context
from TNS import fetch_from_tns
from TNS import poll_tns
from TNS import tns_crossmatch
from TNS import tns_runner
import unittest


class AnnotationsDumpTest(unittest.TestCase):
    """Placeholder"""


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    