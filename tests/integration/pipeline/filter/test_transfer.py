"""
Test the csv transfer function from transfer_to_main using a temporary local database.
"""

import os, sys
import unittest.main
from unittest import TestCase, expectedFailure, mock
import mysql.connector
from mysql.connector.errors import *
sys.path.append('../../../../common')
import settings
sys.path.append('../../../../pipeline/filter')
from transfer import fetch_attrs, transfer_csv

config = {
        'user':     'ztf',
        'password': 'password456',
        'host':     'localhost',
        'db':       'ztf',
        'port':     3306,
        'charset':  'utf8mb4',
        'allow_local_infile' : True,
        }

table_from = 'things_from'
table_to   = 'things_to'


class RunTransferTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up connection, ensure that the test tables exist and create a record."""
        cls.msl = mysql.connector.connect(**config)
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            # source of the data, order is a2, a1
            query = f"CREATE TABLE IF NOT EXISTS { table_from } "
            query += "( objectId varchar(16) NOT NULL, a2 float, a1 float, PRIMARY KEY (objectId) )"
            cursor.execute(query)
            # sink of the data, order is a1, a2
            query = f"CREATE TABLE IF NOT EXISTS { table_to } "
            query += "( objectId varchar(16) NOT NULL, a1 float, a2 float, PRIMARY KEY (objectId) )"
            cursor.execute(query)
            # insert a record. a2=2.2, a1=1.1
            query = f"INSERT INTO { table_from } ( objectId, a2, a1 ) VALUES ( 'ZTF23abcdef', 2.2, 1.1 )"
            cursor.execute(query)

            # get ride of the old files
            cmd = 'sudo --non-interactive rm /data/mysql/*.txt'
            os.system(cmd)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table and tear down connection"""
        query = f"DROP TABLE { table_from }"
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
        query = f"DROP TABLE { table_to }"
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
        cls.msl.close()

    def test_1_get_attrs(self):
        """Read the attributes of table_to"""
        expected_result = ['objectId', 'a2', 'a1']
        attrs = fetch_attrs(self.msl, table_from)
        # should return three
        self.assertEqual(len(attrs), 3)
        # check objectID re as expected
        for i in range(3):
            self.assertEqual(attrs[i], expected_result[i])

    def test_2_transfer(self):
        """Make CSV and transfer it"""
        attrs = fetch_attrs(self.msl, table_to)
        # ensure that outfile is not present
        try:
            os.remove(f"/data/mysql/{ table_from }.txt")
        except FileNotFoundError:
            pass
        log = mock.MagicMock()
        rc = transfer_csv(self.msl, self.msl, attrs, table_from, table_to, log=log)
        # transfer should return true with no errors
        log.error.assert_not_called()
        self.assertTrue(rc)
        # check the contents of the dest table
        query = f"SELECT * FROM { table_to }"
        cursor = self.msl.cursor(buffered=True, dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        self.assertEqual(result, {'objectId': 'ZTF23abcdef', 'a1': 1.1, 'a2': 2.2})


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
