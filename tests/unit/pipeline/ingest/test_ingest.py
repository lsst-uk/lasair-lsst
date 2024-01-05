import unittest, unittest.mock

import signal
import subprocess
import pickle
import context
import ingest


class IngestTest(unittest.TestCase):

    # check that the sigterm handler sets sigterm raised correctly
    def test_sigterm_handler(self):
        self.assertFalse(ingest.sigterm_raised)
        subprocess.run(['pkill', '-f', 'python3 test_ingest.py'])
        self.assertTrue(ingest.sigterm_raised)

    # test using the image store 
    def test_store_images(self):
        # load up a test alert
        with open('alert_single_visit_sample.bin', 'rb') as f:
            lsst_alert = pickle.load(f)
        diaSourceId = lsst_alert['diaSource']['diaSourceId']
        diaObjectId = lsst_alert['diaObject']['diaObjectId']
        imjd = int(lsst_alert['diaSource']['midPointTai'])
        # use a mock object for the image store
        with unittest.mock.MagicMock() as mock_image_store: 
            result = ingest.store_images(lsst_alert, mock_image_store, diaSourceId, imjd, diaObjectId)
            # check we returned something other than None
            self.assertIsNotNone(result)
            # check we called putCutout twice
            self.assertEqual(mock_image_store.putCutout.call_count, 2)

    # test cassandra insert 
    def test_insert_cassandra(self):
        # load up a test alert
        with open('alert_dp02.bin', 'rb') as f:
            lsst_alert = pickle.load(f)
        alert = {
            'diaObject':                 lsst_alert['DiaObject'],
            'diaSourcesList':            lsst_alert['DiaSourceList'],
            'forcedSourceOnDiaObjectsList':      lsst_alert['ForcedSourceOnDiaObjectList'],
        }
        with unittest.mock.patch('ingest.executeLoad') as mock_executeLoad:
            mock_executeLoad.return_value = None
            cassandra_session = True
            ingest.insert_cassandra(alert, cassandra_session)
            # executeLoad should get called twice, once for diaObject and once for forcedSourceOnDiaObjectsList
            self.assertEqual(mock_executeLoad.call_count, 2)     

if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
