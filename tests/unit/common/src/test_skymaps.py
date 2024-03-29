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

# inputs to the test_get_skymap_hits
objlist = ['a12', 'a13', 'a14', 'a15']
ralist  = [188.0, 190.0, 190.0, 194.0]
delist  = [-9.0,  -15.0, -11.0, -19.0]

# output is only from the last one
'a15', contour=66, distsigma ~= 0, probdens=85

class SkymapTest(unittest.TestCase):
    @mock.patch('skymaps.fetch_alerts')
    def test_get_skymap_hits(self, fetch_alerts_mock):
        """Runs the skymap code with the ralist/declist and the bayestar map
        The results should match up with distance and inmoc90 """

        fetch_alerts_mock.return_value = {
                "obj": objlist, 
                "ra":ralist, 
                "de":delist, 
                "distance":distance
                }

        # a database connection is not needed because the alerts are listed above
        database = None

        gw = {'mw_id': 1, 
            'event_tai':60000, 
            'area90':500, 
            'otherId':'skymapdata',  # fetch from test cache
            'version':'.',           # fetch from test cache
            'params':None,
            }
        skymaphits = skymaps.get_skymap_hits(database, gw, verbose=True)
        print(skymaphits)
        # should be 1 in the skymaphits from the 4 input
        self.assertTrue(len(skymaphits['diaObjectId']) == 1)
        contour   = skymaphits['contour'][0]
        distsigma = skymaphits['distsigma'][0]
        probdens  = skymaphits['probdens'][0]

        self.assertTrue(abs(contour-66.31) < 0.1)
        self.assertTrue(distsigma < 0.01)
        self.assertTrue(abs(probdens-85.06) < 0.1)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
