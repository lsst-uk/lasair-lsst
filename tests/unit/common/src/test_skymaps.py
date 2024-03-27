"""
Test for the get_skymap_hits, using the skymap and code in
https://emfollow.docs.ligo.org/userguide/tutorial/multiorder_skymaps.html
The most probable RA/Dec is 194.304 -17.856
Map   file is bayestar.multiorder.fits
Moc90 file is bayestar.multiorder.moc
"""
import sys
import unittest
import unittest.mock as mock
from mocpy import MOC
sys.path.append('../../../../common/src')
import skymaps

objlist = ['a12', 'a13', 'a14', 'a15']
ralist  = [188.0, 190.0, 190.0, 194.0]
delist  = [-9.0,  -15.0, -11.0, -19.0]
distance =[None, 20.348, None, 34.784]
inmoc90 = [False, False, True, True]

class SkymapTest(unittest.TestCase):
    @mock.patch('skymaps.fetch_alerts')
    def test_get_skymap_hits(self, fetch_alerts_mock):

        fetch_alerts_mock.return_value = {
                "obj": objlist, 
                "ra":ralist, 
                "de":delist, 
                "distance":distance
                }

        database = None
        gw = {'mw_id': 1, 
            'event_tai':60000, 
            'area90':500, 
            'otherId':'skymapdata',  # fetch from test cache
            'version':'.',           # fetch from test cache
            'params':None,
            }
        skymaphits = skymaps.get_skymap_hits(database, gw)
        print(skymaphits)
        # should be 2 in the skymaphits from the 4 input
        #   skymaphits['diaObjectId'] should be ['a14', 'a15'], 
        #   skymaphits['distsigma'] should be   [None, approx zero]}


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
