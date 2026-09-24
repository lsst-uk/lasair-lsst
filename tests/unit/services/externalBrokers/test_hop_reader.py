import sys
import io
import context
import unittest, unittest.mock
from unittest.mock import patch

sys.modules['hop'] = unittest.mock.Mock()
sys.modules['hop.auth'] = unittest.mock.Mock()
sys.modules['hop.io'] = unittest.mock.Mock()
from hop_reader import HopReader


class HopReaderTest(unittest.TestCase):

    @patch("hop_reader.HopReader.poll")
    @patch("hop_reader.HopReader.parse")
    def test_retry_until_success(self, mock_parse, mock_poll):
        settings = {
            'MODULE': '',
            'CODE': '',
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
        }
        hr = HopReader(settings)
        mock_poll.side_effect = [
            TimeoutError(),
            TimeoutError(),
            {"unparsed annotation": {"id": 1}},
        ]
        mock_parse.return_value = {"annotation": {"id": 1}}
        result = hr.next_ann()
        self.assertEqual(result, {"annotation": {"id": 1}})
        self.assertEqual(mock_poll.call_count, 3)

    @patch("hop_reader.HopReader.poll")
    def test_retry_failure(self, mock_poll):
        settings = {
            'MODULE': '',
            'CODE': '',
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
            'RETRIES': 2
        }
        hr = HopReader(settings)
        mock_poll.side_effect = TimeoutError()
        result = hr.next_ann()
        self.assertEqual(result, None)
        self.assertEqual(mock_poll.call_count, 2)

    def test_poll_success(self):
        mock_alert = unittest.mock.MagicMock()
        mock_alert.content = "test"
        mock_stream = unittest.mock.MagicMock()
        mock_stream.__next__.return_value = mock_alert
        settings = {
            'MODULE': '',
            'CODE': '',
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
            'RETRIES': 2
        }
        hr = HopReader(settings)
        hr.hop_stream = mock_stream
        result = hr.poll()
        self.assertEqual(result, "test")

    def test_poll_failure(self):
        mock_stream = unittest.mock.MagicMock()
        mock_stream.__next__.side_effect = StopIteration
        settings = {
            'MODULE': '',
            'CODE': '',
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
            'RETRIES': 2
        }
        hr = HopReader(settings)
        hr.hop_stream = mock_stream
        result = hr.poll()
        self.assertIn('error', result)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    
