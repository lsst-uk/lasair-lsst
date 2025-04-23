#import context
import os, sys, json, time
import unittest
from random import random
import mysql.connector
from multiprocessing import Process
sys.path.append('../../../../common/src')
from manage_status import manage_status, timer

config = {
    'user':     'ztf',
    'password': 'password456',
    'host':     'localhost',
    'db':       'ztf',
    'port':     3306,
    'charset':  'utf8mb4',
}

# multiprocessing test
nproc  = 4
niter  = 10
deltaT = 1
nid    = 7

def func(msl, iproc):
    msl = mysql.connector.connect(**config)
    ms = manage_status(msl, 'test_lasair_statistics')
    for i in range(niter):
        time.sleep(deltaT*random())
        ms.add({'count':1},    nid)

class CommonManageStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up connection, ensure that the test table exists and create a test object."""
        cls.msl = mysql.connector.connect(**config)
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            query = "CREATE TABLE IF NOT EXISTS test_lasair_statistics "
            query += "(nid int NOT NULL, name VARCHAR(32), value FLOAT DEFAULT 0, "
            query += "PRIMARY key (nid,name))"
            cursor.execute(query)

    @classmethod
    def tearDownClass(cls):
        """Get rid of the test table and tear down connection"""
        query = "DROP TABLE test_lasair_statistics"
        with cls.msl.cursor(buffered=True, dictionary=True) as cursor:
            cursor.execute(query)
        cls.msl.close()

    def test_manage_status(self):
        return
        msl = mysql.connector.connect(**config)
        ms = manage_status(msl, 'test_lasair_statistics')
        ms.set({'banana':5, 'orange':6}, 6)
        ms.add({'apple':12, 'pear':7},   6)
        ms.add({'apple':12, 'pear':1},   6)
        status = ms.read(6)
#        print(status)
        self.assertTrue(status['banana'] == 5)
        self.assertTrue(status['orange'] == 6)
        self.assertTrue(status['apple']  == 24)
        self.assertTrue(status['pear']   == 8)

    def test_delete(self):
        return
        """Test deleting an nid"""
        msl = mysql.connector.connect(**config)
        ms = manage_status(msl, 'test_lasair_statistics')
        ms.set({'lemon':1, 'lime':2}, 7)
        ms.delete(nid=7)
        status = ms.read(7)
        self.assertEqual(status, {})

    def test_multiprocessing(self):
        return
        msl = None
        procs = []
        for iproc in range(nproc):
            proc = Process(target=func, args=(msl, iproc,))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()

        msl = mysql.connector.connect(**config)
        ms = manage_status(msl, 'test_lasair_statistics')
        status = ms.read(nid)
#        print(status)
        self.assertTrue(status['count'] == nproc*niter)

    def test_timer(self):
        return
        td = timer('mango')
        time.sleep(1)

        td.on()
        time.sleep(1)
        td.off()

        time.sleep(1)

        td.on()
        time.sleep(1)
        td.off()

        msl = mysql.connector.connect(**config)
        ms = manage_status(msl, 'test_lasair_statistics')
        td.add2ms(ms, 6)
        status = ms.read(6)
#        print(td.name, status[td.name])
        self.assertTrue(abs(status[td.name] - 2) < 0.01)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
