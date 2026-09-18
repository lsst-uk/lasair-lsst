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
        '--directory'  : 'sample_hopskotch_output/gw',
        '--contours'   : '10,50,90',
    }
    ret = readGW.handleDataDict(dataDict, options, logger=None)

  def test1_readIcecube(self):
    dataDict = json.loads(open('sample_hopskotch_input/icecube.json').read())
    skymap = open('sample_input/icecube_hopskotch_skymap.fits', 'rb').read()
    dataDict['event']['skymap'] = skymap
    options = {
        '--superevents': False,
        '--directory'  : 'sample_hopskotch_output/gw',
        '--contours'   : '10,50,90',
    }
    ret = readIcecube.handleDataDict(dataDict, options, logger=None)



if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()
