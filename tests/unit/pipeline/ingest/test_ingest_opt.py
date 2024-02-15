# tests for optimised ingest
# this is termporary and will go away once optised version is merged

import unittest, unittest.mock
from unittest.mock import patch

import signal
import subprocess
#import pickle
import context
import ingest_opt as ingest


test_alert = {
    'DiaObject': { 'diaObjectId': 1998903343203749723, },
    'DiaSource': { 'diaSourceId': 181071530527032103, 'midPointTai': 57095.171263959775 },
    'DiaSourceList': [ { 'diaSourceId': 176546782480695886, 'midPointTai': 57070.34313563427 }, { 'diaSourceId': 176891668354564641, 'midPointTai': 57072.3425344742 } ],
    'ForcedSourceOnDiaObjectList': [ {}, {} ],
    'cutoutDifference': b'foo',
    'cutoutTemplate': b'bar',
}

class IngestOptTest(unittest.TestCase):

    # check that the sigterm handler sets sigterm raised correctly
    def test_sigterm_handler(self):
        self.assertFalse(ingest.sigterm_raised)
        subprocess.run(['pkill', '-f', 'python3 test_ingest_opt.py'])
        self.assertTrue(ingest.sigterm_raised)

    # test using the image store 
    def test_store_images(self):
        mock_image_store = unittest.mock.MagicMock()
        diaSourceId = test_alert['DiaSource']['diaSourceId']
        diaObjectId = test_alert['DiaObject']['diaObjectId']
        imjd = int(test_alert['DiaSource']['midPointTai'])
        result = ingest.store_images(test_alert, mock_image_store, diaSourceId, imjd, diaObjectId)
        # check we returned something other than None
        self.assertIsNotNone(result)
        # check we called putCutoutAsync twice
        self.assertEqual(mock_image_store.putCutoutAsync.call_count, 2)

    @patch('ingest_opt.executeLoadAsync')
    def test_insert_cassandra(self, mock_executeLoadAsync):
        alert = {
            'diaObject':                 test_alert['DiaObject'],
            'diaSourcesList':            test_alert['DiaSourceList'],
            'forcedSourceOnDiaObjectsList':      test_alert['ForcedSourceOnDiaObjectList'],
        }
        cassandra_session = True
        ingest.insert_cassandra(alert, cassandra_session)
        # executeLoad should get called three times, once for diaObject and once for each list
        self.assertEqual(mock_executeLoadAsync.call_count, 3)     

    @patch('ingest_opt.insert_cassandra_multi')
    @patch('ingest_opt.store_images')
    def test_handle_alert(self, mock_store_images, mock_insert_cassandra_multi):
        mock_store_images.return_value = [ unittest.mock.MagicMock() ]
        mock_insert_cassandra_multi.return_value = [ unittest.mock.MagicMock() ]
        image_store = True
        mock_producer = unittest.mock.MagicMock()
        topic_out = None
        cassandra_session = None
        result = ingest.handle_alert(test_alert, image_store, mock_producer, topic_out, cassandra_session)
        # check the return values
        self.assertEqual(result, (2, 2))
        # store_images should get called once
        mock_store_images.assert_called_once()
        # insert_cassandra_multi should get called once
        mock_insert_cassandra_multi.assert_called_once()
        # producer.produce should get called once
        mock_producer.produce.assert_called_once()
    
    @patch('ingest_opt.log')
    def test_end_batch(self, mock_log):
        mock_consumer = unittest.mock.MagicMock()
        mock_producer = unittest.mock.MagicMock()
        mock_ms = unittest.mock.MagicMock()
        ingest.end_batch(mock_consumer, mock_producer, mock_ms, 1, 2, 2)
        # log message should get sent
        mock_log.info.assert_called_once()
        # producer should get flushed
        mock_producer.flush.assert_called_once()
        # consumer offsets should get committed
        mock_consumer.commit.assert_called_once()
        # status page should get updated
        mock_ms.add.assert_called_once()


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
