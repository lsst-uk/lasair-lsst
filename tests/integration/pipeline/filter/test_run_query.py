"""
Test the run_query function from run_active_queries using a temporary local database.
"""

import sys
import unittest.main
from unittest import TestCase, expectedFailure, mock
import mysql.connector
from mysql.connector.errors import *
sys.path.append('../../../../pipeline/filter')
sys.path.append('../../../../common')
import settings
from run_active_queries import run_query

config = {
        'user':     'ztf',
        'password': 'password456',
#        'password': '123password',
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
        """Set up connection, ensure that the test table exists and create a test object."""
        cls.msl = mysql.connector.connect(**config)
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            query = f"CREATE TABLE IF NOT EXISTS { table } "
            query += "( objectId varchar(16) NOT NULL, RA float, PRIMARY KEY (objectId) )"
            cursor.execute(query)
            query = f"INSERT INTO { table } ( objectId, RA ) VALUES ( 'ZTF23abcdef', 23.123 )"
            cursor.execute(query)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table and tear down connection"""
        query = f"DROP TABLE { table }"
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
        cls.msl.close()

    def test_1_run_query(self):
        """Read from the database"""
        expected_result = {'objectId': 'ZTF23abcdef', 'RA': 23.123}
        query = f"SELECT * FROM { table } WHERE RA BETWEEN 23 and 24"
        querydict['real_sql'] = query
        query_results = run_query(querydict, RunQueryTest.msl)
        # should return one result
        self.assertEqual(len(query_results), 1)
        # check objectID and RA are as expected
        self.assertEqual(query_results[0]['objectId'], expected_result['objectId'])
        self.assertEqual(query_results[0]['RA'], expected_result['RA'])

    def test_2_syntax_err(self):
        """What happens with query syntax error"""
        query = f"SELECT * FROM { table } WWWWWWWWWWWWWWWWWWWWHERE id=1"
        querydict['real_sql'] = query
        # patch out the send email function
        with mock.patch('run_active_queries.send_email') as mock_email:
            query_results = run_query(querydict, RunQueryTest.msl)
            #TODO: actually check something here

    def test_3_timeout_err(self):
        """Timeout error"""
        query = f"SET STATEMENT max_statement_time=2 FOR SELECT SLEEP(4)"
        querydict['real_sql'] = query
        # patch out the send email function
        with mock.patch('run_active_queries.send_email') as mock_email:
            query_results = run_query(querydict, RunQueryTest.msl)
            #TODO: actually check something here

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
