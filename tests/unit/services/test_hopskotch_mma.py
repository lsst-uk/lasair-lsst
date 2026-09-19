import sys
import json
import context
import unittest.main
from unittest import TestCase
sys.path.append('../../../../common')
import settings

sys.path.append('../../../../services/externalBrokers/mma_hopskotch')
import readGW, readIcecube

class MmaHopskotchTest(TestCase):
  def test0_readGW(self):
    dataDict = json.loads(open('sample_hopskotch_input/igwn.json').read())
    skymap = open('sample_hopskotch_input/igwn_skymap.fits', 'rb').read()
    dataDict['event']['skymap'] = skymap
    options = {
        '--superevents': False,
        '--directory'  : '/tmp/LVK',
        '--contours'   : '10,50,90',
    }
    ret = readGW.handleDataDict(dataDict, options, logger=None)
    # assert that every file in /tmp/LVK is identical 
    # to those in sample_hopskotch_output/LVK

  def test1_readIcecube(self):
    dataDict = json.loads(open('sample_hopskotch_input/Icecube.json').read())
    skymap = open('sample_input/Icecube_hopskotch_skymap.fits', 'rb').read()
    dataDict['event']['skymap'] = skymap
    options = {
        '--superevents': False,
        '--directory'  : '/tmp/Icecube',
        '--contours'   : '10,50,90',
    }
    ret = readIcecube.handleDataDict(dataDict, options, logger=None)
    # assert that every file in /tmp/Icecube is identical 
    # to those in sample_hopskotch_output/Icecube

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()
