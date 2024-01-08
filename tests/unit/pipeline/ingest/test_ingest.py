import unittest, unittest.mock

import signal
import subprocess
import pickle
import context
import ingest


test_alert = {
    'DiaObject': { 'diaObjectId': 1998903343203749723, },
    'DiaSource': { 'diaSourceId': 181071530527032103, 'midPointTai': 57095.171263959775 },
    'DiaSourceList': [ {}, {} ],
    'ForcedSourceOnDiaObjectList': [ {}, {} ],
    'cutoutDifference': b'foo',
    'cutoutTemplate': b'bar',
}

class IngestTest(unittest.TestCase):

    # check that the sigterm handler sets sigterm raised correctly
    def test_sigterm_handler(self):
        self.assertFalse(ingest.sigterm_raised)
        subprocess.run(['pkill', '-f', 'python3 test_ingest.py'])
        self.assertTrue(ingest.sigterm_raised)

    # test using the image store 
    def test_store_images(self):
        diaSourceId = test_alert['DiaSource']['diaSourceId']
        diaObjectId = test_alert['DiaObject']['diaObjectId']
        imjd = int(test_alert['DiaSource']['midPointTai'])
        # use a mock object for the image store
        with unittest.mock.MagicMock() as mock_image_store: 
            result = ingest.store_images(test_alert, mock_image_store, diaSourceId, imjd, diaObjectId)
            # check we returned something other than None
            self.assertIsNotNone(result)
            # check we called putCutout twice
            self.assertEqual(mock_image_store.putCutout.call_count, 2)

    # test cassandra insert 
    def test_insert_cassandra(self):
        alert = {
            'diaObject':                 test_alert['DiaObject'],
            'diaSourcesList':            test_alert['DiaSourceList'],
            'forcedSourceOnDiaObjectsList':      test_alert['ForcedSourceOnDiaObjectList'],
        }
        with unittest.mock.patch('ingest.executeLoad') as mock_executeLoad:
            mock_executeLoad.return_value = None
            cassandra_session = True
            ingest.insert_cassandra(alert, cassandra_session)
            # executeLoad should get called three times, once for diaObject and once for each list
            self.assertEqual(mock_executeLoad.call_count, 3)     

if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
