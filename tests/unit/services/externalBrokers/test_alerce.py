import sys
import context
import unittest, unittest.mock
from unittest.mock import patch
from proxy_annotators import get_log_stream, load_annotator, get_next_annotation, process_annotator, ProxyAnnotator


class AlerceTest(unittest.TestCase):

    settings_lc = {
            "CODE": "alerce.alerce_lc",
            "SERVERS": "",
            "ALERCE_NAME": "",
            "ALERCE_PASSWORD": "",
            "schema_filename": "../../../../services/externalBrokers/proxy/alerce/stamp_classifier_rubin.avsc",
            }

    settings_stamp = {
            "CODE": "alerce.alerce_stamp",
            "SERVERS": "",
            "ALERCE_NAME": "",
            "ALERCE_PASSWORD": "",
            }

    @patch('alerce.alerce_lc.Consumer')
    def test_load_alerce_lc(self, mock_consumer):
        result = load_annotator(AlerceTest.settings_lc)
        self.assertIsInstance(result, ProxyAnnotator)

    @patch('alerce.alerce_lc.Consumer')
    @patch('alerce.alerce_lc.fastavro.schemaless_reader')
    def test_next_ann_lc(self, mock_reader, mock_consumer):
        from alerce import alerce_lc
        a = alerce_lc.Annotator(AlerceTest.settings_lc)
        fake_record = {
            'oid': 1,
            'lc_classification': {
                'class': 'mango',
                'probabilities': {
                    'mango': 1
                }
            },
        }
        mock_reader.return_value.__next__.return_value = fake_record
        mock_consumer.return_value.poll.return_value.value.return_value = b''
        result = a.next_ann()
        self.assertEqual(result['annotation']['classification'], "mango")

    @patch('alerce.alerce_lc.Consumer')
    def test_end_stream_lc(self, mock_consumer):
        from alerce import alerce_lc
        a = alerce_lc.Annotator(AlerceTest.settings_lc)
        mock_consumer.return_value.poll.return_value = None
        result = a.next_ann()
        self.assertEqual(result, {'error': 'End of stream'})

    @patch('alerce.alerce_stamp.Consumer')
    def test_load_alerce_stamp(self, mock_consumer):
        result = load_annotator(AlerceTest.settings_stamp)
        self.assertIsInstance(result, ProxyAnnotator)

    @patch('alerce.alerce_stamp.Consumer')
    @patch('alerce.alerce_lc.fastavro.reader')
    def test_next_ann_stamp(self, mock_reader, mock_consumer):
        from alerce import alerce_stamp
        a = alerce_stamp.Annotator(AlerceTest.settings_stamp)
        fake_record = {
            'objectId': 1,
            'probabilities': {
                'kiwi': 0.9
            }
        }
        mock_reader.return_value.__next__.return_value = fake_record
        mock_consumer.return_value.poll.return_value.value.return_value = b''
        result = a.next_ann()
        self.assertEqual(result['annotation']['classification'], "kiwi")

    @patch('alerce.alerce_stamp.Consumer')
    def test_end_stream_stamp(self, mock_consumer):
        from alerce import alerce_stamp
        a = alerce_stamp.Annotator(AlerceTest.settings_stamp)
        mock_consumer.return_value.poll.return_value = None
        result = a.next_ann()
        self.assertEqual(result, {'error': 'End of stream'})


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    
