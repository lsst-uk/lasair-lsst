import context
import cutoutStore
import unittest
from unittest.mock import MagicMock

class CutoutStoreTest(unittest.TestCase):
    """Placeholder"""

    def test_getCutout(self):
        """Test getting a cutout (normal flow)."""
        mock_session = MagicMock()
        mock_session.execute.return_value = [type("row", (), {"cutoutimage": b"data"})]
        cs = cutoutStore.cutoutStore(mock_session)
        imagedata = cs.getCutout("somecutoutid", 1234)
        mock_session.execute.assert_called_once()
        self.assertEqual(b"data", imagedata)

    def test_getCutout_not_found(self):
        """Test trying to get a cutout that is not found."""
        mock_session = MagicMock()
        mock_session.execute.return_value = []
        cs = cutoutStore.cutoutStore(mock_session)
        imagedata = cs.getCutout("somecutoutid", 1234)
        mock_session.execute.assert_called_once()
        self.assertEqual(None, imagedata)

    def test_putCutout(self):
        """Test adding a cutout."""
        mock_session = MagicMock()
        cs = cutoutStore.cutoutStore(mock_session)
        cs.putCutout("somecutoutid", 1234, "objectid", b"blob")
        self.assertEqual(2, mock_session.execute.call_count)

    def test_putCutoutAsync(self):
        """Test adding a cutout (async)."""
        mock_session = MagicMock()
        mock_session.execute_async.return_value = "future"
        cs = cutoutStore.cutoutStore(mock_session)
        future = cs.putCutoutAsync("somecutoutid", 1234, "objectid", b"blob")
        self.assertEqual(2, mock_session.execute_async.call_count)
        self.assertEqual("future", future)

    def test_trim_cutout(self):
        pass

    def test_compression(self):
        pass


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
