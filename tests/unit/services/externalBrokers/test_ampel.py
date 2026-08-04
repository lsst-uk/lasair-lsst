import sys
import context
import unittest, unittest.mock
from proxy_annotators import load_annotator, ProxyAnnotator

sys.modules['hop'] = unittest.mock.Mock()
sys.modules['hop.auth'] = unittest.mock.Mock()
sys.modules['hop.io'] = unittest.mock.Mock()
import ampel_extragal
import ampel_infant


class Ampel(unittest.TestCase):

    def test_load_ampel_extragal(self):
        result = load_annotator({
            "CODE": "hopskotch.ampel_extragal",
            "MODULE": "ampel.lsst.extragalactic-transients",
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
             }
        )
        self.assertIsInstance(result, ProxyAnnotator)

    def test_load_ampel_infant(self):
        result = load_annotator({
            "CODE": "hopskotch.ampel_infant",
            "MODULE": "ampel.lsst.extragalactic-infants",
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
             }
        )
        self.assertIsInstance(result, ProxyAnnotator)

    def test_parse_ampel_extralgal(self):
        settings = {
            "CODE": "hopskotch.ampel_extragal",
            "MODULE": "ampel.lsst.extragalactic-transients",
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
        }
        message = {
            'object': {'id': 1},
            'classification': [{'models': [{'probabilities': {'__t_': 1}}]}]
        }
        a = ampel_extragal.Annotator(settings)
        result = a.parse(message)
        self.assertEqual(result['annotation']['classdict'], '{"t": 1.0}')

    def test_parse_ampel_infant(self):
        settings = {
            "CODE": "hopskotch.ampel_infant",
            "MODULE": "ampel.lsst.extragalactic-infants",
            'SCIMMA_AUTH_USERNAME': '',
            'SCIMMA_AUTH_PASSWORD': '',
        }
        message = {
            'object': {'id': 1},
            'features': [{'features': {'test': 2}}]
        }
        a = ampel_infant.Annotator(settings)
        result = a.parse(message)
        self.assertEqual(result['annotation']['classdict'], '{"test": 2}')


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    
