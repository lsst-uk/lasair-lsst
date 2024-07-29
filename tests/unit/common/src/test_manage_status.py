#import context
import os, sys, time
import unittest
import unittest.mock
#from random import random
#import mysql.connector
#from multiprocessing import Process
sys.path.append('../../../../common/src')
from manage_status import manage_status, timer


class CommonManageStatusTest(unittest.TestCase):

    def test_read(self):
        msl = unittest.mock.MagicMock()
        ms = manage_status(msl, 'test_lasair_statistics')
        ms.read(6)
        (args,) = msl.cursor.return_value.execute.call_args.args
        self.assertRegex(args, "SELECT name,value FROM test_lasair_statistics WHERE nid=6")

    def test_set(self):
        msl = unittest.mock.MagicMock()
        ms = manage_status(msl, 'test_lasair_statistics')
        ms.set({'banana':5, 'orange':6}, 6)
        (args,) = msl.cursor.return_value.execute.call_args.args
        self.assertRegex(args, "REPLACE INTO test_lasair_statistics \(nid,name,value\) VALUES \(6,.banana.,5([\.0]*)\),\(6,.orange.,6[\.0]*\)")

    def test_delete(self):
        msl = unittest.mock.MagicMock()
        ms = manage_status(msl, 'test_lasair_statistics')
        ms.delete(nid=6)
        (args,) = msl.cursor.return_value.execute.call_args.args
        self.assertRegex(args, "DELETE FROM test_lasair_statistics  WHERE nid=6")

    def test_add(self):
        msl = unittest.mock.MagicMock()
        ms = manage_status(msl, 'test_lasair_statistics')
        ms.add({'apple':12, 'pear':7},   6)
        calls = msl.cursor.return_value.execute.call_args_list
        args = [call.args[0] for call in calls]
        self.assertRegex(args[0], "INSERT INTO test_lasair_statistics \(nid,name,value\) VALUES \(6,.apple.,12([\.0]*)\) ON DUPLICATE KEY UPDATE value=value\+12")
        self.assertRegex(args[1], "INSERT INTO test_lasair_statistics \(nid,name,value\) VALUES \(6,.pear.,7([\.0]*)\) ON DUPLICATE KEY UPDATE value=value\+7")

    def test_timer(self):
        """Test that the timer class does timing approximately correctly"""
        td = timer('mango')
        td.on()
        time.sleep(0.1)
        td.off()
        time.sleep(0.2)
        td.on()
        time.sleep(0.1)
        td.off()
        self.assertAlmostEqual(td.elapsed, 0.2, places=1)

    def test_timer_add(self):
        msl = unittest.mock.MagicMock()
        ms = manage_status(msl, 'test_lasair_statistics')
        td = timer('mango')
        td.elapsed = 0.5
        td.add2ms(ms, 8)
        (args,) = msl.cursor.return_value.execute.call_args.args
        self.assertRegex(args, "INSERT INTO test_lasair_statistics \(nid,name,value\) VALUES \(8,.mango(.*).,0.5([\.0]*)\) ON DUPLICATE KEY UPDATE value=value\+0.5")


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
