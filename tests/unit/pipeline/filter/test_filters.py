import unittest, unittest.mock
from unittest.mock import patch

import context
import datetime, json
import numpy as np
from filters import dispose_kafka
from filters import crap_converter


class FilterTest(unittest.TestCase):
    def test_crap_converter(self):
        """ Make sure that JSO can't reject the odd types it may get """
        c = {
            'date': datetime.datetime(2026, 2, 8, 9, 19, 19),
            'np1': np.float32(1.5),
            'np2': np.float64(1.5),
            'np3': np.int32(10),
            'np4': np.int64(10),
            'none': None,
            'cmpx': complex(2,3),
        }
        expect = """{"date": "2026-02-08 09:19:19", "np1": "1.5", "np2": 1.5, "np3": "10", "np4": "10", "none": null, "cmpx": "Unexpected type in json.dumps:<class 'complex'>"}"""
        out = json.dumps(c, default=crap_converter)
        self.assertEqual(out, expect)

    def test_dispose_kafka_produce(self):
        """ Test that the right call is made to manage_status when disposing kafka under quota """
        mock_producer      = unittest.mock.MagicMock()
        mock_manage_status = unittest.mock.MagicMock()
        query_results = [{'apple':1, 'pear':2}]   # list of output results

        query = {'bytes_produced': 100,
                 'byte_quota'    : 200,           # under quota
                 'topic_name':'tpc'}
        nid = 0
        dispose_kafka(mock_producer, query_results, query, mock_manage_status, nid)
        expect = {'tpc_bytes_produced': 23,       # expect production
                  'tpc_alerts_produced':1}
        mock_manage_status.add.assert_called_with(expect, 0)

    def test_dispose_kafka_reject(self):
        """ Test that the right call is made to manage_status when disposing kafka over quota """
        mock_producer      = unittest.mock.MagicMock()
        mock_manage_status = unittest.mock.MagicMock()
        query_results = [{'apple':1, 'pear':2}]   # list of output results

        query = {'bytes_produced': 300,
                 'byte_quota'    : 200,           # over quota
                 'topic_name':'tpc'}
        nid = 0
        dispose_kafka(mock_producer, query_results, query, mock_manage_status, nid)
        expect = {'tpc_bytes_rejected': 23,       # expect rejection
                  'tpc_alerts_rejected':1}
        mock_manage_status.add.assert_called_with(expect, 0)

if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
