"""
Test of Cassandra usage for cutout images

Requires a functional cassandra running on localhost.
"""

import os
import unittest.main
from unittest import TestCase, expectedFailure
from cassandra.cluster import Cluster
import sys
sys.path.append('../../../common/src')
import cutoutStore

# the real keyspace is called 'cutouts' but we use a different one for the test
keyspace = 'cutouts_test'

# This file is part of the test and is in the repo
cutoutId = '181071530527032078_cutoutTemplate'

# Make the keyspace and the table
create_keyspace = """
CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3 };
""" % keyspace

create_table = """
CREATE TABLE IF NOT EXISTS cutouts (
   cutoutId      ascii,
   objectId      bigint,
   imjd          int,
   cutoutimage   blob,
  PRIMARY KEY (imjd, cutoutId)
 );
"""

class CassandraCutoutTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up connection, keyspace, table."""
        cluster = Cluster(['localhost'])
        cls.session = cluster.connect()
        cls.session.default_timeout = 30
        cls.session.execute(create_keyspace)
        cls.session.set_keyspace(keyspace)
        cls.session.execute(create_table)
        cls.osc = cutoutStore.cutoutStore(cls.session)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table, keyspace, connection"""
        cls.session.execute("DROP TABLE cutouts")
        cls.session.execute("DROP KEYSPACE %s" % keyspace, timeout=300)
        cls.session.shutdown()

    def test_1_write(cls):
        """Write something to the database"""
        filename = cutoutId + '.fits'
        cutoutBlob = open(filename, 'rb').read()
        
        # put into cassandra
        imjd = 60000
        objectId = 1234567890
        cls.osc.putCutout(cutoutId, imjd, objectId, cutoutBlob)

        # look for it in there
        query = "SELECT cutoutId from cutouts where cutoutId='%s' and imjd=%d" % (cutoutId, imjd)
        rows = cls.session.execute(query)
        cls.assertEqual(len(list(rows)), 1)

    def test_2_read(cls):
        """Read something from the database"""
        imjd = 60000
        cutout = cls.osc.getCutout(cutoutId, imjd)
        fp = open(cutoutId + '_copy.fits', 'wb')
        fp.write(cutout)
        fp.close()
        # assert files are the same
        cmd = 'cmp %s.fits %s_copy.fits' % (cutoutId, cutoutId)
        cls.assertEqual(os.system(cmd), 0)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
