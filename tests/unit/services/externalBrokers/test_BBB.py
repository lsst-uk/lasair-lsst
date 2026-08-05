import sys
import context
import unittest, unittest.mock
from unittest.mock import patch
from proxy_annotators import get_log_stream, load_annotator, get_next_annotation, process_annotator, ProxyAnnotator


class BBBTest(unittest.TestCase):

    @patch('filter.BBB_fast_SN.lasair_consumer')
    def test_load_BBB_fast_SN(self, mock_consumer):
        result = load_annotator({
            "CODE": "filter.BBB_fast_SN",
            "TOPIC": "",
             }
        )
        self.assertIsInstance(result, ProxyAnnotator)

    @patch('filter.BBB_fast_SN.lasair_consumer')
    def test_next_ann(self, mock_consumer):
        from filter import BBB_fast_SN
        a = BBB_fast_SN.Annotator({
            "CODE": "filter.BBB_fast_SN",
            "TOPIC": "",
             }
        )
        fake_msg = '{"diaObjectId": "1"}'
        mock_consumer.poll.return_value.error.return_value = None
        mock_consumer.poll.return_value.value.return_value = fake_msg
        a.consumer = mock_consumer
        result = a.next_ann()
        self.assertEqual(result['annotation']['classification'], "Exp")


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    
