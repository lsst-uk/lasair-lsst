"""
Test of Cassandra usage for cutout images

Requires a functional cassandra running on localhost.
"""

import unittest.main
from unittest import TestCase, expectedFailure
from cassandra.cluster import Cluster
import sys
sys.path.append('../../../common/src')
import objectStoreCass

keyspace = 'cutouts'
keyspace = 'junk'

# This file is part of the test and is in the repo
objectId = '181071530527032078_cutoutTemplate'

# Make the keyspace and the table
create_keyspace = """
CREATE KEYSPACE %s WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3 };
""" % keyspace

create_table = """
CREATE TABLE IF NOT EXISTS cutouts (
   cutout        ascii,
   cutoutimage   blob,
  PRIMARY KEY (cutout)
 );
"""

class CassandraCutoutTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up connection, keyspace, table."""
        cluster = Cluster(['localhost'])
        self.session = cluster.connect()
        self.session.execute(create_keyspace)
        self.session.set_keyspace(keyspace)
        self.session.execute(create_table)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table, keyspace, connection"""
        self.session.execute("DROP TABLE cutouts")
        self.session.execute("DROP KEYSPACE %s" % keyspace)
        self.session.close()

    def test_1_write(self):
        """Write something to the database"""
        query = f"INSERT INTO { conf['table'] } ( id, foo ) VALUES ( 1, 0.123 )"
        with ExampleIntegrationTest.connection.cursor() as cursor:
            count = cursor.execute(query)
            self.assertEqual(count, 1)
        # read the file
        filename = objectId + '.fits'
        objectBlob = open(filename, 'rb').read()
        
        # put into cassandra
        self.osc = objectStoreCass.objectStoreCass()
        self.osc.putObject(objectId, objectBlob)

        # look for it in there
        query = "SELECT cutout from cutouts where cutout='%s'" % objectId
        rows = self.session.execute(sql)
        self.assertEqual(len(rows), 1)

    def test_2_read(self):
        """Read something from the database"""
        cutout = self.osc.getObject(objectId)
        fp = open(objectId + '_copy.fits', 'wb')
        fp.write(cutout)
        fp.close()
        # assert files are the same
        cmd = 'cmp %s.fits %s_copy.fits' % (objectId, objectId)
        self.assertEqual(os.system(cmd), 0)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
