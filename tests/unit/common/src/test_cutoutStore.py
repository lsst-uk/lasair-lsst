import context
import cutoutStore
import os
import threading
import time
import unittest
from unittest.mock import MagicMock, patch


class CutoutStoreTest(unittest.TestCase):
    """Tests for the Cassandra based cutoutStore."""

    def test_trim_fits(self):
        """Test trimming cutout FITS data."""
        data = open('sample_cutout.fits', 'rb').read()
        trimmed_data = cutoutStore.trim_fits(data)
        # Our sample file should contain 3 2880 byte blocks, one header and two data.
        self.assertEqual(8640, len(trimmed_data))

    def test_getCutout(self):
        """Test getting a cutout (normal flow)."""
        mock_session = MagicMock()
        mock_session.execute.return_value = [type("row", (), {"cutoutimage": b"data"})]
        cs = cutoutStore.cutoutStore(mock_session)
        imagedata = cs.getCutout("somecutoutid")
        mock_session.execute.assert_called_once()
        self.assertEqual(b"data", imagedata)

    def test_getCutout_not_found(self):
        """Test trying to get a cutout that is not found."""
        mock_session = MagicMock()
        mock_session.execute.return_value = []
        cs = cutoutStore.cutoutStore(mock_session)
        imagedata = cs.getCutout("somecutoutid")
        mock_session.execute.assert_called_once()
        self.assertEqual(None, imagedata)

    def test_putCutout(self):
        """Test adding a cutout."""
        mock_session = MagicMock()
        cs = cutoutStore.cutoutStore(mock_session)
        cs.putCutout("somecutoutid", "objectid", True, b"blob")
        self.assertEqual(2, mock_session.execute.call_count)

    def test_putCutout_trim_and_compress(self):
        """Test adding a cutout with trimming and compression."""
        data_in = open('sample_cutout.fits', 'rb').read()
        data_out = open('sample_cutout_trimmed.fits.lz4', 'rb').read()
        mock_session = MagicMock()
        cs = cutoutStore.cutoutStore(mock_session)
        cs.trim = True
        cs.compress = True
        cs.putCutout("somecutoutid", "objectid", True, data_in)
        ((sql, cutout), kwargs) = mock_session.execute.call_args_list[0]
        self.assertEqual("somecutoutid", cutout[0])
        self.assertEqual(data_out, cutout[1])

    def test_putCutoutAsync(self):
        """Test adding a cutout asynchronously."""
        mock_session = MagicMock()
        mock_future = MagicMock()
        mock_session.execute_async.return_value = mock_future
        cs = cutoutStore.cutoutStore(mock_session)
        future = cs.putCutoutAsync("somecutoutid", "objectid", True, b"blob")
        self.assertEqual(2, mock_session.execute_async.call_count)
        self.assertEqual([mock_future, mock_future], future)

    def test_putCutoutAsync_trim_and_compress(self):
        """Test adding a cutout asynchronously with trimming and compression."""
        data_in = open('sample_cutout.fits', 'rb').read()
        data_out = open('sample_cutout_trimmed.fits.lz4', 'rb').read()
        mock_session = MagicMock()
        cs = cutoutStore.cutoutStore(mock_session)
        cs.trim = True
        cs.compress = True
        cs.putCutoutAsync("somecutoutid", "objectid", True, data_in)
        ((sql, cutout), kwargs) = mock_session.execute_async.call_args_list[0]
        self.assertEqual("somecutoutid", cutout[0])
        self.assertEqual(data_out, cutout[1])

    def test_compression(self):
        """"Test getting compressed image data."""
        compressed_data = \
            b'\x04"M\x18h@%\x00\x00\x00\x00\x00\x00\x00\x8e\x10\x00\x00\x00odata a\x01\x00\x07Paaaaa\x00\x00\x00\x00'
        mock_session = MagicMock()
        mock_session.execute.return_value = [type("row", (), {"cutoutimage": compressed_data})]
        cs = cutoutStore.cutoutStore(mock_session)
        cs.compress = True
        imagedata = cs.getCutout("somecutoutid")
        mock_session.execute.assert_called_once()
        self.assertEqual(b'data aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', imagedata)
        pass


class SharedCutoutStoreTest(unittest.TestCase):
    """Tests for the per-process shared cutoutStore used by the website."""

    def setUp(self):
        cutoutStore.reset_shared_store()
        patcher = patch('cutoutStore.Cluster')
        self.mockClusterClass = patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(cutoutStore.reset_shared_store)

    def test_many_requests_create_one_cluster(self):
        # ARRANGE
        session = self.mockClusterClass.return_value.connect.return_value
        session.is_shutdown = False
        session.execute.return_value = [type("row", (), {"cutoutimage": b"data"})]

        # ACT
        images = [cutoutStore.get_shared_store().getCutout("id") for _ in range(200)]

        # ASSERT
        self.assertEqual(1, self.mockClusterClass.call_count)
        self.assertEqual([b"data"] * 200, images)

    def test_reset_shuts_down_cluster_and_next_request_reconnects(self):
        # ARRANGE
        firstCluster, secondCluster = MagicMock(), MagicMock()
        self.mockClusterClass.side_effect = [firstCluster, secondCluster]
        cutoutStore.get_shared_store()

        # ACT
        cutoutStore.reset_shared_store()
        store = cutoutStore.get_shared_store()

        # ASSERT
        firstCluster.shutdown.assert_called_once()
        secondCluster.shutdown.assert_not_called()
        self.assertIs(secondCluster.connect.return_value, store.session)

    def test_failed_connection_is_retried_on_next_request(self):
        # ARRANGE
        brokenCluster, workingCluster = MagicMock(), MagicMock()
        brokenCluster.connect.side_effect = Exception('no hosts available')
        workingCluster.connect.return_value.is_shutdown = False
        self.mockClusterClass.side_effect = [brokenCluster, workingCluster]

        # ACT
        firstStore = cutoutStore.get_shared_store()
        secondStore = cutoutStore.get_shared_store()

        # ASSERT
        self.assertIsNone(firstStore.session)
        brokenCluster.shutdown.assert_called_once()
        self.assertIs(workingCluster.connect.return_value, secondStore.session)

    def test_shut_down_session_is_recreated_on_next_request(self):
        # ARRANGE
        firstCluster, secondCluster = MagicMock(), MagicMock()
        firstCluster.connect.return_value.is_shutdown = False
        secondCluster.connect.return_value.is_shutdown = False
        self.mockClusterClass.side_effect = [firstCluster, secondCluster]
        firstStore = cutoutStore.get_shared_store()

        # ACT
        firstStore.session.is_shutdown = True
        secondStore = cutoutStore.get_shared_store()

        # ASSERT
        self.assertEqual(2, self.mockClusterClass.call_count)
        self.assertIs(secondCluster.connect.return_value, secondStore.session)

    def test_failed_connection_shuts_its_cluster_down_at_once(self):
        # ARRANGE
        brokenCluster = MagicMock()
        brokenCluster.connect.side_effect = Exception('no hosts available')
        self.mockClusterClass.return_value = brokenCluster

        # ACT
        cutoutStore.get_shared_store()

        # ASSERT
        brokenCluster.shutdown.assert_called_once()

    def test_discarding_the_current_store_makes_next_request_reconnect(self):
        # ARRANGE
        firstCluster, secondCluster = MagicMock(), MagicMock()
        firstCluster.connect.return_value.is_shutdown = False
        secondCluster.connect.return_value.is_shutdown = False
        self.mockClusterClass.side_effect = [firstCluster, secondCluster]
        failedStore = cutoutStore.get_shared_store()

        # ACT
        cutoutStore.discard_shared_store(failedStore)
        nextStore = cutoutStore.get_shared_store()

        # ASSERT
        firstCluster.shutdown.assert_called_once()
        self.assertIs(secondCluster.connect.return_value, nextStore.session)

    def test_discarding_a_stale_store_keeps_the_current_one(self):
        # ARRANGE
        firstCluster, secondCluster = MagicMock(), MagicMock()
        firstCluster.connect.return_value.is_shutdown = False
        secondCluster.connect.return_value.is_shutdown = False
        self.mockClusterClass.side_effect = [firstCluster, secondCluster]
        staleStore = cutoutStore.get_shared_store()
        cutoutStore.discard_shared_store(staleStore)
        currentStore = cutoutStore.get_shared_store()

        # ACT
        cutoutStore.discard_shared_store(staleStore)

        # ASSERT
        self.assertIs(currentStore, cutoutStore.get_shared_store())
        secondCluster.shutdown.assert_not_called()

    def test_concurrent_requests_create_one_cluster(self):
        # ARRANGE
        THREADCOUNT = 20
        session = self.mockClusterClass.return_value.connect.return_value
        session.is_shutdown = False
        self.mockClusterClass.return_value.connect.side_effect = lambda: time.sleep(0.05) or session
        barrier = threading.Barrier(THREADCOUNT)
        stores = []

        def request():
            barrier.wait()
            stores.append(cutoutStore.get_shared_store())

        threads = [threading.Thread(target=request) for _ in range(THREADCOUNT)]

        # ACT
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # ASSERT
        self.assertEqual(1, self.mockClusterClass.call_count)
        self.assertEqual(1, len(set(map(id, stores))))

    @unittest.skipUnless(hasattr(os, 'fork'), 'needs os.fork')
    def test_forked_child_builds_its_own_cluster(self):
        # ARRANGE
        parentSession = self.mockClusterClass.return_value.connect.return_value
        parentSession.is_shutdown = False
        parentStore = cutoutStore.get_shared_store()

        # ACT
        pid = os.fork()
        if pid == 0:
            # THE CHILD MUST NEVER RETURN INTO THE TEST RUNNER
            exitCode = 2
            try:
                childStore = cutoutStore.get_shared_store()
                isOwnStore = childStore is not parentStore and self.mockClusterClass.call_count == 2
                exitCode = 0 if isOwnStore else 1
            finally:
                os._exit(exitCode)
        _, status = os.waitpid(pid, 0)

        # ASSERT
        self.assertEqual(0, os.waitstatus_to_exitcode(status))
        self.assertIs(parentStore, cutoutStore.get_shared_store())


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
