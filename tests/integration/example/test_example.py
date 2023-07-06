"""
Example integrtation test.

Can be used as a template for writing integration tests.

Requires a functional database running on localhost.
"""

import unittest.main
from unittest import TestCase, expectedFailure
import pymysql.cursors

conf = {
        'host': 'localhost',
        'user': 'ztf',
        'password': 'password456',
        'db': 'ztf',
        'charset': 'utf8mb4',
        'table': 'example123'
        }

class ExampleIntegrationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up connection and ensure that the test table exists."""
        cls.connection = pymysql.connect(
                host = conf.host,
                user = conf.user,
                password = conf.password,
                db = conf.db,
                charset = conf.charset,
                cursorclass=pymysql.cursors.DictCursor)
        query = f"CREATE TABLE IF NOT EXISTS { conf.table }( 'id' int NOT NULL, 'foo' float, PRIMARY KEY (id) )"
        try:
            with cls.connection.cursor() as cursor:
                cursor.execute(query)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table and tear down connection"""
        query = f"DROP TABLE { conf.table }"
        try:
            with cls.connection.cursor() as cursor:
                cursor.execute(query)
        cls.connection.close()

    def test_1_do_nothing(self):
        pass

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()


