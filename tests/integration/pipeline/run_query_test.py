"""
Example integration test.

Can be used as a template for writing integration tests.

Requires a functional database running on localhost.
"""

import sys
import unittest.main
from unittest import TestCase, expectedFailure
import mysql.connector
from mysql.connector.errors import *
sys.path.append('../../../pipeline/filter')
from run_active_queries import run_query, send_email
sys.path.append('../../../common')

config = {
        'user':     'ztf',
#        'password': 'password456',
        'password': '123password',
        'host':     'localhost',
        'db':       'ztf',
        'port':     3306,
        'charset':  'utf8mb4',
        }

table = 'test_objects'

querydict = {
        'real_sql'   : None,
        'topic_name' : 'test_topic',
        'active'     : None,
        'email'      : 'roydavidwilliams@gmail.com'
}

class RunQueryTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up connection and ensure that the test table exists."""
        cls.msl = mysql.connector.connect(**config)
        query = f"CREATE TABLE IF NOT EXISTS { table } "
        query += "( objectId varchar(16) NOT NULL, RA float, PRIMARY KEY (objectId) )"
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
        query = f"INSERT INTO { table } ( objectId, RA ) VALUES ( 'ZTF23abcdef', 23.123 )"
        with RunQueryTest.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
        
    def test_2_run_query(self):
        """Read something from the database"""
        query = f"SELECT * FROM { table } WHERE RA BETWEEN 23 and 24"
        querydict['real_sql'] = query
        query_results = run_query(querydict, RunQueryTest.msl)
        print(query_results)

    def test_3_syntax_err(self):
        """What happens with query syntax error"""
        query = f"SELECT * FROM { table } WWWWWWWWWWWWWWWWWWWWHERE id=1"
        querydict['real_sql'] = query
        with RunQueryTest.msl.cursor(buffered=True, dictionary=True) as cursor:
            query_results = run_query(querydict, RunQueryTest.msl)
            print(query_results)

    def test_4_timeout_err(self):
        """Timeout error"""
        query = f"SET STATEMENT max_statement_time=2 FOR SELECT SLEEP(4)"
        querydict['real_sql'] = query
        with RunQueryTest.msl.cursor(buffered=True, dictionary=True) as cursor:
            query_results = run_query(querydict, RunQueryTest.msl)
            print(query_results)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
