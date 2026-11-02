"""Unit tests for the fits cutout view in lasair/utils.py."""
import importlib
import os
import sys
import types
import unittest
from unittest import mock

from cassandra.cluster import NoHostAvailable

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../webserver')))


class FakeHttpResponse(dict):
    def __init__(self, content, content_type=None):
        super().__init__()
        self.content = content
        self.content_type = content_type


def module(**attributes):
    result = types.ModuleType('stub')
    result.__dict__.update(attributes)
    return result


def load_utils():
    """Load lasair.utils with framework and infrastructure edges stubbed, keeping the real cutoutStore."""
    modules = {
        'ephem': module(),
        'src.db_connect': module(),
        'django': module(),
        'django.shortcuts': module(get_object_or_404=mock.Mock()),
        'django.http': module(
            HttpResponse=FakeHttpResponse, HttpResponseRedirect=object, JsonResponse=object),
        'django.template': module(),
        'django.template.context_processors': module(csrf=lambda request: {}),
        'django.conf': module(settings=module()),
        'dateutil': module(parser=module()),
        'dateutil.parser': module(),
        'pandas': module(),
        'lasair.lightcurves': module(lightcurve_fetcher=object),
        'astropy': module(time=module()),
        'astropy.time': module(Time=object),
    }
    with mock.patch.dict(sys.modules, modules):
        sys.modules.pop('lasair.utils', None)
        utils = importlib.import_module('lasair.utils')
    return utils


class FitsViewTest(unittest.TestCase):
    """Tests for the fits view that serves cutout images."""

    def setUp(self):
        self.utils = load_utils()
        store = self.utils.cutoutStore
        store.reset_shared_store()
        patcher = mock.patch.object(store, 'Cluster')
        self.mockClusterClass = patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(store.reset_shared_store)
        self.session = self.mockClusterClass.return_value.connect.return_value
        self.session.is_shutdown = False

    def test_many_cutout_requests_share_one_cluster(self):
        # ARRANGE
        self.session.execute.return_value = [type("row", (), {"cutoutimage": b"SIMPLE  =  T"})]

        # ACT
        responses = [self.utils.fits(None, '123_cutoutDifference') for _ in range(200)]

        # ASSERT
        self.assertEqual(1, self.mockClusterClass.call_count)
        self.mockClusterClass.return_value.shutdown.assert_not_called()
        self.assertEqual(b"SIMPLE  =  T", responses[-1].content)
        self.assertEqual('image/fits', responses[-1].content_type)
        self.assertEqual(
            'attachment; filename="123_cutoutDifference.fits"',
            responses[-1]['Content-Disposition'])

    def test_failed_lookup_returns_empty_body(self):
        # ARRANGE
        self.session.execute.side_effect = Exception('read timeout')

        # ACT
        response = self.utils.fits(None, '123_cutoutDifference')

        # ASSERT
        self.assertEqual('', response.content)

    def test_bad_cutout_row_keeps_the_connection(self):
        # ARRANGE
        self.session.execute.side_effect = Exception('lz4 frame is corrupt')

        # ACT
        self.utils.fits(None, '123_cutoutDifference')
        self.utils.fits(None, '123_cutoutDifference')

        # ASSERT
        self.assertEqual(1, self.mockClusterClass.call_count)
        self.mockClusterClass.return_value.shutdown.assert_not_called()

    def test_request_after_failed_lookup_reconnects(self):
        # ARRANGE
        brokenCluster, workingCluster = mock.MagicMock(), mock.MagicMock()
        brokenCluster.connect.return_value.is_shutdown = False
        brokenCluster.connect.return_value.execute.side_effect = NoHostAvailable('no hosts available', {})
        workingSession = workingCluster.connect.return_value
        workingSession.is_shutdown = False
        workingSession.execute.return_value = [type("row", (), {"cutoutimage": b"SIMPLE  =  T"})]
        self.mockClusterClass.side_effect = [brokenCluster, workingCluster]

        # ACT
        self.utils.fits(None, '123_cutoutDifference')
        response = self.utils.fits(None, '123_cutoutDifference')

        # ASSERT
        brokenCluster.shutdown.assert_called_once()
        self.assertEqual(b"SIMPLE  =  T", response.content)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
