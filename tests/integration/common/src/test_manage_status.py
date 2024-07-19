#import context
import os, sys, json, time
import unittest
from random import random
from multiprocessing import Process
sys.path.append('../../../../common')
sys.path.append('../../../../common/src')
from manage_status import manage_status, timer

# multiprocessing test
nproc  = 4
niter  = 10
deltaT = 1
nid    = 7

def func(iproc):
    ms = manage_status()
    for i in range(niter):
        time.sleep(deltaT*random())
        ms.add({'count':1},    nid)

class CommonManageStatusTest(unittest.TestCase):
    def test_manage_status(self):
        ms = manage_status()
        ms.set({'banana':5, 'orange':6}, 6)
        ms.add({'apple':12, 'pear':7},   6)
        ms.add({'apple':12, 'pear':1},   6)
        status = ms.read(6)
#        print(status)
        self.assertTrue(status['banana'] == 5)
        self.assertTrue(status['orange'] == 6)
        self.assertTrue(status['apple']  == 24)
        self.assertTrue(status['pear']   == 8)

    def test_multiprocessing(self):
        procs = []
        for iproc in range(nproc):
            proc = Process(target=func, args=(iproc,))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()

        ms = manage_status()
        status = ms.read(nid)
#        print(status)
        self.assertTrue(status['count'] == nproc*niter)
        ms.delete(nid)

    def test_timer(self):
        td = timer('mango')
        time.sleep(1)

        td.on()
        time.sleep(1)
        td.off()

        time.sleep(1)

        td.on()
        time.sleep(1)
        td.off()

        ms = manage_status()
        td.add2ms(ms, 6)
        status = ms.read(6)
#        print(td.name, status[td.name])
        self.assertTrue(abs(status[td.name] - 2) < 0.01)

        # delete the play area
        ms.delete(6)

if __name__ == '__main__':
    import xmlrunner
    ms = manage_status()
    ms.delete()
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
