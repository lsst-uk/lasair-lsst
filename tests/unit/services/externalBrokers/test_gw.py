import context
#from gw import readGW
import unittest


class GWTest(unittest.TestCase):
    """Placeholder"""


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    