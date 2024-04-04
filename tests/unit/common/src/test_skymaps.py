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

class SkymapTest(unittest.TestCase):
    @mock.patch('skymaps.fetch_alerts')
    def test_get_skymap_hits(self, fetch_alerts_mock):
        """Runs the skymap code with the ralist/declist and the bayestar map
        The results should match up with distance and inmoc90 """

        # inputs to the test_get_skymap_hits
        fetch_alerts_mock.return_value = {
                "obj"      : ['a12', 'a13', 'a14', 'a15'],
                "ra"       :[188.0, 190.0, 190.0, 194.0],
                "de"       :[-9.0,  -15.0, -11.0, -19.0],
                "distance" :[23.510,20.350,27.440,34.780]
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
        #print(skymaphits)
        # should be 1 in the skymaphits from the 4 input
        # output should be {'diaObjectId': ['a15'], 'contour': [66.31], 'distance': [34.78], 
        #    'probdens2': [85.0601], 'probdens3': [85.0601]}
        self.assertTrue(len(skymaphits['diaObjectId']) == 1)
        contour   = skymaphits['contour'][0]
        distance  = skymaphits['distance'][0]
        probdens2  = skymaphits['probdens2'][0]
        probdens3  = skymaphits['probdens3'][0]

        self.assertTrue(abs(contour-66.31) < 0.1)
        self.assertTrue(abs(distance-34.78) < 0.1)
        self.assertTrue(abs(probdens2-85.06) < 0.1)
        self.assertTrue(abs(probdens3-85.06) < 0.1)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
