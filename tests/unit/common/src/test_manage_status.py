import context
import os, sys, json, time
import unittest
from manage_status import manage_status, timer

class CommonManageStatusTest(unittest.TestCase):
    def test_manage_status(self):
        # put the status files in here
        os.system('mkdir play')

        ms = manage_status('play/status')
        ms.set({'banana':5, 'orange':6}, 6)
        ms.add({'apple':12, 'pear':7},   6)
        ms.add({'apple':12, 'pear':1},   6)

        ms.add({'apple':1, 'pear':7},    7)
        ms.add({'apple':1, 'pear':7},    7)
        ms.set({'banana':5, 'orange':6}, 7)
        ms.set({'banana':4, 'orange':7}, 7)
        ms.set({'banana':3, 'orange':8}, 7)

        status = ms.read(6)
        self.assertEqual(status['banana'], 5)
        self.assertEqual(status['orange'], 6)
        self.assertEqual(status['apple'], 24)
        self.assertEqual(status['pear'],   8)

        status = ms.read(7)
        self.assertEqual(status['banana'], 3)
        self.assertEqual(status['orange'], 8)
        self.assertEqual(status['apple'],  2)
        self.assertEqual(status['pear'],  14)

        td = timer('mango')
        time.sleep(1)

        td.on()
        time.sleep(1)
        td.off()

        time.sleep(1)

        td.on()
        time.sleep(1)
        td.off()

        td.add2ms(ms, 6)
        status = ms.read(6)
        print(td.name, status[td.name])
        self.assertTrue(abs(status[td.name] - 2) < 0.01)

        # delete the play area
        os.system('rm -r play')

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
