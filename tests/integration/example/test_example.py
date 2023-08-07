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
                host = conf['host'],
                user = conf['user'],
                password = conf['password'],
                db = conf['db'],
                charset = conf['charset'],
                cursorclass=pymysql.cursors.DictCursor)
       # 'id' int NOT NULL, 'foo' float, PRIMARY KEY (id) ) 
        query = f"CREATE TABLE IF NOT EXISTS { conf['table'] }( id int NOT NULL, foo float, PRIMARY KEY (id) )"
        with cls.connection.cursor() as cursor:
            cursor.execute(query)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table and tear down connection"""
        query = f"DROP TABLE { conf['table'] }"
        with cls.connection.cursor() as cursor:
            cursor.execute(query)
        cls.connection.close()

    def test_1_write(self):
        """Write something to the database"""
        query = f"INSERT INTO { conf['table'] } ( id, foo ) VALUES ( 1, 0.123 )"
        with ExampleIntegrationTest.connection.cursor() as cursor:
            count = cursor.execute(query)
            self.assertEqual(count, 1)
        
    def test_2_read(self):
        """Read something from the database"""
        query = f"SELECT * FROM { conf['table'] } WHERE id=1"
        with ExampleIntegrationTest.connection.cursor() as cursor:
            count = cursor.execute(query)
            self.assertEqual(count, 1)
            result = cursor.fetchone()
            self.assertEqual(result.get('id'), 1)
            self.assertEqual(result.get('foo'), 0.123)
        

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()


