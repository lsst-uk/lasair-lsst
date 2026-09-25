import sys
import json
import context
import unittest.main
from pathlib import Path
from unittest import TestCase
sys.path.append('../../../../common')
import settings

sys.path.append('../../../../services/externalBrokers/mma_hopskotch')
import readLVK, readIcecube

class MmaHopskotchTest(TestCase):
  def test0_readLVK(self):
    dataDict = json.loads(open('sample_hopskotch_input/igwn.json').read())
    skymap = open('sample_hopskotch_input/igwn_skymap.fits', 'rb').read()
    dataDict['event']['skymap'] = skymap
    options = {
        '--superevents': False,
        '--directory'  : '/tmp/LVK',
        '--contours'   : '10,50,90',
    }
    ret = readLVK.handleDataDict(dataDict, options, logger=None)
    dir = '/LVK/MS260814i/20260814T080340_preliminary/'
    expect_dir = 'sample_hopskotch_output' + dir
    actual_dir = '/tmp' + dir

    self.assertEqual(
        Path(expect_dir + '/meta.yaml').read_bytes(),
        Path(actual_dir + '/meta.yaml').read_bytes(),
        "Files differ: LVK meta.yaml",
    )
    self.assertEqual(
        Path(expect_dir + '/90.moc').read_bytes(),
        Path(actual_dir + '/90.moc').read_bytes(),
        "Files differ: LVK 90.moc",
    )

  def test1_readIcecube(self):
    dataDict = json.loads(open('sample_hopskotch_input/icecube.json').read())
    skymap = open('sample_hopskotch_input/icecube_skymap.fits', 'rb').read()
    options = {
        '--superevents': False,
        '--directory'  : '/tmp/Icecube',
        '--contours'   : '10,50,90',
    }
    ret = readIcecube.handleDataDict(dataDict, options, logger=None)
    dir = '/Icecube/260801a/final/'
    expect_dir = 'sample_hopskotch_output' + dir
    actual_dir = '/tmp' + dir

    self.assertEqual(
        Path(expect_dir + '/meta.yaml').read_bytes(),
        Path(actual_dir + '/meta.yaml').read_bytes(),
        "Files differ: Icecube meta.yaml",
    )
    self.assertEqual(
        Path(expect_dir + '/90.moc').read_bytes(),
        Path(actual_dir + '/90.moc').read_bytes(),
        "Files differ: Icecube 90.moc",
    )

if __name__ == '__main__':
  import xmlrunner
  runner = xmlrunner.XMLTestRunner(output='test-reports')
  unittest.main(testRunner=runner)
  unittest.main()
