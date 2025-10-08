import unittest, unittest.mock
from unittest.mock import patch
import psutil
import subprocess
import context
import ingest as ingest

test_alert = {
    'diaObject': {'diaObjectId': 1998903343203749723, 'ra':123, 'dec':23},

    # 3 diaSources
    'diaSource': {'diaSourceId': 181071530527032103, 'midpointMjdTai': 57075.0, 'ra':123, 'dec':23},
    'prvDiaSources': [
        {'diaSourceId': 176891668354564642, 'midpointMjdTai': 57074.0, 'ra':123, 'dec':23},
        {'diaSourceId': 176891668354564641, 'midpointMjdTai': 57072.0, 'ra':123, 'dec':23},
        {'diaSourceId': 176546782480695887, 'midpointMjdTai': 57071.0, 'ra':123, 'dec':23},
        {'diaSourceId': 176546782480695886, 'midpointMjdTai': 57070.0, 'ra':123, 'dec':23},
        ],

    # zero of these
    'prvDiaForcedSources': [
        {'diaSourceId': 176546782480695886, 'midpointMjdTai': 57074.0, 'ra':123, 'dec':23},
        {'diaSourceId': 176546782480695886, 'midpointMjdTai': 57073.0, 'ra':123, 'dec':23},
        {'diaSourceId': 176546782480695886, 'midpointMjdTai': 57069.0, 'ra':123, 'dec':23},
        {'diaSourceId': 176546782480695886, 'midpointMjdTai': 57067.0, 'ra':123, 'dec':23},
        ],
    'prvDiaNondetectionLimits': [],
    'ssObject': {},

    'cutoutDifference': b'foo',
    'cutoutTemplate': b'bar',
}


class IngestTest(unittest.TestCase):

    def test_sigterm_handler(self):
        """Check that the sigterm handler sets sigterm raised correctly"""
        ingester = ingest.Ingester('', '', '', 1, ms=True)
        self.assertFalse(ingester.sigterm_raised)
        psutil.Process().terminate()
        self.assertTrue(ingester.sigterm_raised)

    def test_store_images(self):
        """Test using the image store"""
        mock_image_store = unittest.mock.MagicMock()
        mock_image_store.putCutoutAsync.return_value = ["future1", "future2"]
        diaSourceId = test_alert['diaSource']['diaSourceId']
        diaObjectId = test_alert['diaObject']['diaObjectId']
        isDiaObject = True
        imageStore = ingest.ImageStore(image_store=mock_image_store)
        result = imageStore.store_images(test_alert, diaSourceId, diaObjectId, isDiaObject)
        # we should get 4 futures back (2 per call)
        self.assertEqual(4, len(result))
        # check we called putCutoutAsync twice
        self.assertEqual(mock_image_store.putCutoutAsync.call_count, 2)

    def test_store_images_no_store(self):
        """Test that the image store warns and returns empty list if attempting to use it when image_store is None"""
        mock_log = unittest.mock.MagicMock()
        with self.assertRaises(SystemExit) as cm:
            imageStore = ingest.ImageStore(log=mock_log)
            # check that the exit code was not 0
            self.assertNotEqual(cm.exception.code, 0)
        mock_log.error.assert_called_with('ERROR: Cannot store cutouts')

    def test_store_images_error(self):
        """Test that using the image store raises an exception on error"""
        diaSourceId = test_alert['diaSource']['diaSourceId']
        diaObjectId = test_alert['diaObject']['diaObjectId']
        isDiaObject = True
        mock_image_store = unittest.mock.MagicMock()
        mock_log = unittest.mock.MagicMock()
        mock_image_store.putCutoutAsync.side_effect = Exception('test error')
        imageStore = ingest.ImageStore(log=mock_log, image_store=mock_image_store)
        self.assertRaises(Exception, imageStore.store_images, test_alert, diaSourceId, diaObjectId, isDiaObject)
        mock_log.error.assert_called_with('ERROR in ingest/store_images: test error')

    @patch('ingest.ImageStore')
    @patch('ingest.Cluster')
    @patch('ingest.Producer')
    @patch('ingest.DeserializingConsumer')
    def test_setup(self,
                   mock_consumer,
                   mock_producer,
                   mock_cluster,
                   mock_image_store):
        ingester = ingest.Ingester('', '', '', 1, ms=True)
        ingester.setup()
        self.assertEqual(mock_image_store.call_count, 1)
        self.assertEqual(mock_cluster.call_count, 1)
        self.assertEqual(mock_cluster.return_value.connect.call_count, 1)
        self.assertEqual(mock_cluster.return_value.connect.return_value.set_keyspace.call_count, 1)
        self.assertEqual(mock_producer.call_count, 1)
        self.assertEqual(mock_consumer.call_count, 1)
        self.assertEqual(mock_consumer.return_value.subscribe.call_count, 1)

    @patch('ingest.executeLoadAsync')
    def test_insert_cassandra(self, mock_executeLoadAsync):
        alert = {
            'diaObject': test_alert['diaObject'],
            'diaSourcesList': [test_alert['diaSource']] + test_alert['prvDiaSources'], # list concatenation
            'diaForcedSourcesList': test_alert['prvDiaForcedSources'],
            'diaNondetectionLimitsList': test_alert['prvDiaNondetectionLimits'],
            'ssObject': test_alert['ssObject'],
        }
        ingester = ingest.Ingester('', '', '', 1, cassandra_session=True, ms=True)
        ingester._insert_cassandra(alert)
        # executeLoad should get called three times, once for diaObject and once for each nonempty list
        self.assertEqual(mock_executeLoadAsync.call_count, 3)

    @patch('ingest.Ingester._insert_cassandra_multi')
    def test_handle_alert(self, mock_insert_cassandra_multi):
        mock_insert_cassandra_multi.return_value = [unittest.mock.MagicMock()]
        mock_image_store = unittest.mock.MagicMock()
        mock_producer = unittest.mock.MagicMock()
        ingester = ingest.Ingester('', '', '', 1, image_store=mock_image_store, producer=mock_producer, ms=True)
        result = ingester._handle_alert(test_alert)
        # check the return values
        # 5 diaSources with 4 sent to DB
        # 4 diaForcedSources with 2 sent to DB
        self.assertEqual(result, (1, 0, 0, 5, 4, 4, 2))   
        # store_images should get called once
        mock_image_store.store_images.assert_called_once()
        # insert_cassandra_multi should get called once
        mock_insert_cassandra_multi.assert_called_once()
        # producer.produce should get called once
        mock_producer.produce.assert_called_once()

    def test_end_batch(self):
        mock_log = unittest.mock.MagicMock()
        mock_consumer = unittest.mock.MagicMock()
        mock_producer = unittest.mock.MagicMock()
        mock_ms = unittest.mock.MagicMock()
        ingester = ingest.Ingester('', '', '', 1, log=mock_log, producer=mock_producer, consumer=mock_consumer,
                                   ms=mock_ms)
        nAlert             = 1
        nDiaObject         = 1
        nNoDiaObject       = 0
        nSSObject          = 0
        nDiaSource         = 5
        nDiaSourceDB       = 4
        nDiaForcedSource   = 4
        nDiaForcedSourceDB = 2
        ingester._end_batch(nAlert, nDiaObject, nNoDiaObject, nSSObject, 
                            nDiaSource, nDiaSourceDB, nDiaForcedSource, nDiaForcedSourceDB)
        # log message should get sent
        mock_log.info.assert_called_once()
        # producer should get flushed
        mock_producer.flush.assert_called_once()
        # consumer offsets should get committed
        mock_consumer.commit.assert_called_once()
        # status page should get updated
        self.assertEqual(mock_ms.add.call_count, 1 + len(ingester.timers))

    def test_poll(self):
        mock_log = unittest.mock.MagicMock()
        mock_consumer = unittest.mock.MagicMock()
        mock_consumer.poll.return_value.error.return_value = None
        mock_consumer.poll.return_value.value.return_value = "some alerts here"
        ingester = ingest.Ingester('', '', '', 1, log=mock_log, consumer=mock_consumer, ms=True)
        result = ingester._poll(1)
        # log.error should not get called
        mock_log.error.assert_not_called()
        # check result
        self.assertEqual(result, ["some alerts here"])

    # test that if consumer.poll returns error then we handle it correctly
    def test_poll_error(self):
        mock_log = unittest.mock.MagicMock()
        mock_consumer = unittest.mock.MagicMock()
        mock_consumer.poll.return_value.error.return_value = True
        ingester = ingest.Ingester('', '', '', 1, log=mock_log, consumer=mock_consumer, ms=True)
        result = ingester._poll(1)
        # log.error should get called
        mock_log.error.assert_called_once()
        # check result
        self.assertEqual(result, [])


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
