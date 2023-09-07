import os, sys, json
import unittest, unittest.mock
import context
import app

class SherlockServiceTest(unittest.TestCase):

    def test_query_single(self):
        with unittest.mock.patch('app.classify') as mock_classify:
            pass

    def test_query_multi(self):
        pass

    def test_query_lite(self):
        pass

    def test_query_named(self):
        pass

    def test_query_invalid_dec(self):
        pass

    def test_query_invalid_ra(self):
        pass

    def test_query_invalid_name(self):
        pass


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
