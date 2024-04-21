import unittest, unittest.mock
from unittest.mock import patch
import psutil
import subprocess
import context
import ingest as ingest

test_alert = {
    'DiaObject': {'diaObjectId': 1998903343203749723},
    'DiaSource': {'diaSourceId': 181071530527032103, 'midPointTai': 57095.171263959775},
    'DiaSourceList': [{'diaSourceId': 176546782480695886, 'midPointTai': 57070.34313563427},
                      {'diaSourceId': 176891668354564641, 'midPointTai': 57072.3425344742}],
    'ForcedSourceOnDiaObjectList': [{}, {}],
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

    def test_init_image_store_error(self):
        """Test that image store setup gives a warning and sets image store to None if
        neither settings.CUTOUTCASS nor IMAGEFITS is set"""
        ingest.settings.USE_CUTOUTCASS = False
        ingest.settings.IMAGEFITS = None
        mock_log = unittest.mock.MagicMock()
        imageStore = ingest.ImageStore(log=mock_log)
        self.assertEqual(imageStore.image_store, None)
        mock_log.warn.assert_called_once()

    @patch('ingest.cutoutStore.cutoutStore')
    def test_init_image_store_cass(self, mock_cutoutStore):
        """Test that image store setup calls cutoutStore if settings.CUTOUTCASS is set"""
        ingest.settings.USE_CUTOUTCASS = True
        ingest.settings.IMAGEFITS = None
        imageStore = ingest.ImageStore()
        mock_cutoutStore.assert_called_once()
        self.assertEqual(imageStore.image_store, mock_cutoutStore.return_value)

    @patch('ingest.objectStore.objectStore')
    def test_init_image_store_fits(self, mock_objectStore):
        """Test that image store setup calls objectStore if settings.IMAGEFITS is set"""
        ingest.settings.USE_CUTOUTCASS = False
        ingest.settings.IMAGEFITS = '/tmp/testdir0987654321'
        imageStore = ingest.ImageStore()
        mock_objectStore.assert_called_once()
        self.assertEqual(imageStore.image_store, mock_objectStore.return_value)

    def test_store_images(self):
        """Test using the image store"""
        mock_image_store = unittest.mock.MagicMock()
        diaSourceId = test_alert['DiaSource']['diaSourceId']
        diaObjectId = test_alert['DiaObject']['diaObjectId']
        imjd = int(test_alert['DiaSource']['midPointTai'])
        ingest.settings.USE_CUTOUTCASS = True
        imageStore = ingest.ImageStore(image_store=mock_image_store)
        result = imageStore.store_images(test_alert, diaSourceId, imjd, diaObjectId)
        # check we called putCutoutAsync twice
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_image_store.putCutoutAsync.call_count, 2)

    def test_store_images_no_store(self):
        """Test that the image store warns and returns empty list if attempting to use it when image_store is None"""
        diaSourceId = test_alert['DiaSource']['diaSourceId']
        diaObjectId = test_alert['DiaObject']['diaObjectId']
        imjd = int(test_alert['DiaSource']['midPointTai'])
        mock_log = unittest.mock.MagicMock()
        ingest.settings.USE_CUTOUTCASS = False
        ingest.settings.IMAGEFITS = None
        imageStore = ingest.ImageStore(log=mock_log)
        result = imageStore.store_images(test_alert, diaSourceId, imjd, diaObjectId)
        self.assertEqual(len(result), 0)
        mock_log.warn.assert_called_with('WARNING: Cannot store cutouts. USE_CUTOUTCASS=False IMAGEFITS=None')

    def test_store_images_error(self):
        """Test that using the image store raises an exception on error"""
        diaSourceId = test_alert['DiaSource']['diaSourceId']
        diaObjectId = test_alert['DiaObject']['diaObjectId']
        imjd = int(test_alert['DiaSource']['midPointTai'])
        mock_image_store = unittest.mock.MagicMock()
        mock_log = unittest.mock.MagicMock()
        ingest.settings.USE_CUTOUTCASS = True
        mock_image_store.putCutoutAsync.side_effect = Exception('test error')
        imageStore = ingest.ImageStore(log=mock_log, image_store=mock_image_store)
        self.assertRaises(Exception, imageStore.store_images, test_alert, diaSourceId, imjd, diaObjectId)
        mock_log.error.assert_called_with('ERROR in ingest/store_images: test error')

    @patch('ingest.ImageStore')
    @patch('ingest.Cluster')
    @patch('ingest.Producer')
    @patch('ingest.Consumer')
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
            'diaObject': test_alert['DiaObject'],
            'diaSourcesList': test_alert['DiaSourceList'],
            'forcedSourceOnDiaObjectsList': test_alert['ForcedSourceOnDiaObjectList'],
        }
        ingester = ingest.Ingester('', '', '', 1, cassandra_session=True, ms=True)
        ingester._insert_cassandra(alert)
        # executeLoad should get called three times, once for diaObject and once for each list
        self.assertEqual(mock_executeLoadAsync.call_count, 3)

    @patch('ingest.Ingester._insert_cassandra_multi')
    def test_handle_alert(self, mock_insert_cassandra_multi):
        mock_insert_cassandra_multi.return_value = [unittest.mock.MagicMock()]
        mock_image_store = unittest.mock.MagicMock()
        mock_producer = unittest.mock.MagicMock()
        ingester = ingest.Ingester('', '', '', 1, image_store=mock_image_store, producer=mock_producer, ms=True)
        result = ingester._handle_alert(test_alert)
        # check the return values
        self.assertEqual(result, (2, 2))
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
        ingester._end_batch(1, 2, 2)
        # log message should get sent
        mock_log.info.assert_called_once()
        # producer should get flushed
        mock_producer.flush.assert_called_once()
        # consumer offsets should get committed
        mock_consumer.commit.assert_called_once()
        # status page should get updated
        self.assertEqual(mock_ms.add.call_count, 1 + len(ingester.timers))

    @patch('ingest.fastavro')
    def test_poll(self, mock_avro):
        mock_log = unittest.mock.MagicMock()
        mock_consumer = unittest.mock.MagicMock()
        mock_consumer.poll.return_value.error.return_value = None
        mock_consumer.poll.return_value.value.return_value = b''
        mock_avro.schemaless_reader.return_value = "asdf"
        ingester = ingest.Ingester('', '', '', 1, log=mock_log, consumer=mock_consumer, ms=True)
        result = ingester._poll(1)
        # log.error should not get called
        mock_log.error.assert_not_called()
        # schemaless reader should get called once
        mock_avro.schemaless_reader.assert_called_once()
        # check result
        self.assertEqual(result, ["asdf"])

    # test that if consumer.poll returns error then we handle it correctly
    @patch('ingest.fastavro')
    def test_poll_error(self, mock_avro):
        mock_log = unittest.mock.MagicMock()
        mock_consumer = unittest.mock.MagicMock()
        mock_consumer.poll.return_value.error.return_value = True
        mock_avro.schemaless_reader.return_value = "asdf"
        ingester = ingest.Ingester('', '', '', 1, log=mock_log, consumer=mock_consumer, ms=True)
        result = ingester._poll(1)
        # log.error should get called
        mock_log.error.assert_called_once()
        # schemaless reader should not get called
        mock_avro.schemaless_reader.assert_not_called()
        # check result
        self.assertEqual(result, [])


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
