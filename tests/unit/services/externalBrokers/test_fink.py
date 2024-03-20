import context
# from fink import get_fink
# from fink import get_fink_annotate
import unittest


class AnnotationsDumpTest(unittest.TestCase):
    """Placeholder"""


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    