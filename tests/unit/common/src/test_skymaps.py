"""
Test for the get_skymap_hits, using the skymap and code in
https://emfollow.docs.ligo.org/userguide/tutorial/multiorder_skymaps.html
The most probable RA/Dec is 194.304 -17.856
Map   file is bayestar.multiorder.fits
Moc90 file is bayestar.multiorder.moc
"""
import sys
import unittest, unittest.mock
from mocpy import MOC
sys.path.append('../../../../common/src')
import skymaps

ralist  = [188.0, 190.0, 190.0, 194.0]
delist  = [-9.0, -15.0, -11.0, -19.0]
inmoc90 = [False, False, True, True]

class SkymapTest(unittest.TestCase):
    @mock.patch('skymaps.fetch_alerts')
    @mock.patch('skymaps.mapfilename')
    @mock.patch('skymaps.mocfilename')
    def test_get_skymap_hits(self, fetch_alerts_mock, mapfilename_mock, mocfilename_mock):
        skymaps.fetch_alerts_mock.return_value = {'blah':'blah'}
        skymaps.mapfilename_mock.return_value = 'file.fits'
        skymaps.mocfilename_mock.return_value = 'file.moc'

        database = None
        gw = {'mw_id': 1, 
            'event_tai':60000, 
            'area90':500, 
            'otherId':'GW150914', 
            'version':'final_skymap', 
            'params':None,
            }
        skymaphits = get_skymap_hits(database, gw)
        # checking and assertions here


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
