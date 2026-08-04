import sys
import context
import unittest, unittest.mock
from unittest.mock import patch
from proxy_annotators import get_log_stream, load_annotator, get_next_annotation, process_annotator, ProxyAnnotator


class FinkTest(unittest.TestCase):

    def test_load_fink_snn(self):
        sys.modules['fink_client.consumer'] = unittest.mock.Mock()
        result = load_annotator({
            "CODE": "fink.fink_snn",
            "MODULE": "fink_extragalactic_lt20mag_candidate_lsst",
            "SERVERS": "fake-server",
            "USERNAME": "fake-user",
            "GROUP_ID": "fake-group",
             }
        )
        self.assertIsInstance(result, ProxyAnnotator)

    def test_next_ann(self):
        sys.modules['fink_client.consumer'] = unittest.mock.Mock()
        from fink import fink_snn
        a = fink_snn.Annotator({
            "CODE": "fink.fink_snn",
            "MODULE": "fink_extragalactic_lt20mag_candidate_lsst",
            "SERVERS": "fake-server",
            "USERNAME": "fake-user",
            "GROUP_ID": "fake-group",
            "verbose": False
             }
        )
        fake_alert = {
            "diaSource": {
                "diaObjectId": 123
            },
            "clf": {

            }
        }
        mock_consumer = unittest.mock.MagicMock()
        mock_consumer.poll.return_value = ("fake-topic", fake_alert, 1)
        a.consumer = mock_consumer
        result = a.next_ann()
        self.assertEqual(result['annotation']['classification'], "Unknown")


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    
