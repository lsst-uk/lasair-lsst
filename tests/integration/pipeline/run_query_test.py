"""
Example integration test.

Can be used as a template for writing integration tests.

Requires a functional database running on localhost.
"""

import unittest.main
from unittest import TestCase, expectedFailure
import mysql.connector
from mysql.connector.errors import *

config = {
        'user':     'ztf',
#        'password': 'password456',
        'password': '123password',
        'host':     'localhost',
        'db':       'ztf',
        'port':     3306,
        'charset':  'utf8mb4',
        }

table = 'example123'

class RunQueryTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up connection and ensure that the test table exists."""
        cls.msl = mysql.connector.connect(**config)
        query = f"CREATE TABLE IF NOT EXISTS { table }( id int NOT NULL, foo float, PRIMARY KEY (id) )"
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table and tear down connection"""
        query = f"DROP TABLE { table }"
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
        cls.msl.close()

    def test_1_write(self):
        """Write something to the database"""
        query = f"INSERT INTO { table } ( id, foo ) VALUES ( 1, 0.123 )"
        with RunQueryTest.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
            # Gareth -- cursor doesn't return anything. The test here is no exception
        
    def test_2_read(self):
        """Read something from the database"""
        query = f"SELECT * FROM { table } WHERE id=1"
        with RunQueryTest.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            self.assertEqual(row.get('id'), 1)

    def test_3_syntax_err(self):
        """What happens with query syntax error"""
        query = f"SELECT * FROM { table } WWWWWWWWWWWWWWWWWWWWHERE id=1"
        with RunQueryTest.msl.cursor(buffered=True, dictionary=True) as cursor:
            try:
                result = cursor.execute(query)
            except ProgrammingError as e:
                print('syntax error')

    def test_4_timeout_err(self):
        """Timeout error"""
        query = f"SET STATEMENT max_statement_time=2 FOR SELECT SLEEP(4)"
        with RunQueryTest.msl.cursor(buffered=True, dictionary=True) as cursor:
            try:
                result = cursor.execute(query)
            except DatabaseError as e:
                print('timeout error')

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
