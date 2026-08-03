import sys
import io
import context
import unittest, unittest.mock
from unittest.mock import patch
from proxy_annotators import get_log_stream, load_annotator, get_next_annotation, process_annotator


class ProxyTest(unittest.TestCase):
    def test_get_log_stream_stdout(self):
        stream = get_log_stream(False)
        assert stream is sys.stdout

    @patch("proxy_annotators.importlib.import_module")
    def test_load_annotator(self, mock_import):
        fake_module = unittest.mock.MagicMock()
        fake_module.Annotator.return_value = "annotator"
        mock_import.return_value = fake_module
        result = load_annotator({"CODE": "abc"})
        assert result == "annotator"
        mock_import.assert_called_once_with("abc")

    def test_retry_until_success(self):
        ac = unittest.mock.MagicMock()

        ac.next_ann.side_effect = [
            TimeoutError(),
            TimeoutError(),
            {"annotation": {"id": 1}},
        ]
        result = get_next_annotation(ac)
        assert result == {"annotation": {"id": 1}}

    def test_retry_failure(self):
        ac = unittest.mock.MagicMock()
        ac.next_ann.side_effect = TimeoutError()
        result = get_next_annotation(ac)
        assert result is None

    @patch("proxy_annotators.annotation_util.insert_annotations_kafka")
    def test_process_annotation(self, mock_insert):
        ac = unittest.mock.MagicMock()
        ac.next_ann.side_effect = [
            {"annotation": {"id": 1}},
            {"annotation": {"id": 2}},
            {"error": "done"},
        ]
        inserted = process_annotator(
            ac,
            maxtry=10,
            logger=io.StringIO(),
        )
        assert inserted == 2
        assert mock_insert.call_count == 2

    @patch("proxy_annotators.annotation_util.insert_annotations_kafka")
    def test_process_annotation_end(self, mock_insert):
        ac = unittest.mock.MagicMock()
        ac.next_ann.side_effect = TimeoutError()
        inserted = process_annotator(ac, 10, io.StringIO())
        assert inserted == 0
        assert mock_insert.call_count == 0

    def test_info_message(self):
        ac = unittest.mock.MagicMock()
        ac.next_ann.side_effect = [
            {"info": "waiting"},
            {"error": "done"},
        ]
        logger = io.StringIO()
        process_annotator(ac, 10, logger)
        assert "waiting" in logger.getvalue()


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    
