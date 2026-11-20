"""Unit tests for reading the search query from GET (bookmarkable) or POST (old callers)."""
import importlib
import sys
import types
import unittest
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, '../../../../webserver')

RESULTS = [{'diaObjectId': 1234567890123456789}]
SCHEMA = {'diaObjectId': 'the object id'}


class FakeRequest:
    def __init__(self, method='GET', get=None, post=None):
        self.method = method
        self.GET = get or {}
        self.POST = post or {}
        self.user = types.SimpleNamespace(is_authenticated=False)


def module(**attributes):
    result = types.ModuleType('stub')
    result.__dict__.update(attributes)
    return result


def load_view():
    """Load the search view with framework and infrastructure edges stubbed."""
    render = mock.Mock(side_effect=lambda request, template, context: context)
    favourites_utils = module(
        suppress_hidden=mock.Mock(return_value=(RESULTS, {}, 0)),
        marks_for_table=mock.Mock())
    messages = module(info=mock.Mock())
    modules = {
        'django': module(),
        'django.contrib': module(messages=messages),
        'django.contrib.messages': messages,
        'django.shortcuts': module(render=render),
        'django.db': module(connection=mock.Mock()),
        'lasair.apps.favourites.utils': favourites_utils,
        'lasair.apps.search.utils': module(
            conesearch_impl=mock.Mock(), readcone=mock.Mock(),
            sexra=mock.Mock(), sexde=mock.Mock()),
        'lasair.apps.db_schema.utils': module(get_schema_dict=mock.Mock(return_value=SCHEMA)),
        'src.db_connect': module(remote=mock.Mock()),
        'astrocalc': module(),
        'astrocalc.coords': module(unit_conversion=mock.Mock()),
        'fundamentals': module(),
        'fundamentals.logs': module(emptyLogger=mock.Mock()),
        'gkutils': module(),
        'gkutils.commonutils': module(
            coneSearchHTM=mock.Mock(), FULL=1, QUICK=2, CAT_ID_RA_DEC_COLS=[],
            base26=mock.Mock(), Struct=object),
    }
    with mock.patch.dict(sys.modules, modules):
        sys.modules.pop('lasair.apps.search.views', None)
        view = importlib.import_module('lasair.apps.search.views')
    return view, render, favourites_utils


class SearchViewQueryTest(unittest.TestCase):

    def setUp(self):
        self.view, self.render, self.favourites = load_view()
        patcher = mock.patch.object(
            self.view, 'do_search', return_value=(RESULTS, SCHEMA))
        self.doSearch = patcher.start()
        self.addCleanup(patcher.stop)

    def test_reads_the_query_from_the_get_parameters(self):
        # ARRANGE
        request = FakeRequest('GET', get={'query': 'ZTF22aafxzfb'})

        # ACT
        self.view.search(request)

        # ASSERT
        self.doSearch.assert_called_once_with('ZTF22aafxzfb')
        context = self.render.call_args.args[2]
        self.assertEqual(context['query'], 'ZTF22aafxzfb')
        self.assertEqual(context['results'], RESULTS)

    def test_still_reads_the_query_from_a_post_body(self):
        # ARRANGE
        request = FakeRequest('POST', post={'query': 'SN2022ffg'})

        # ACT
        self.view.search(request)

        # ASSERT
        self.doSearch.assert_called_once_with('SN2022ffg')
        self.assertEqual(self.render.call_args.args[2]['query'], 'SN2022ffg')

    def test_prefers_the_get_query_over_a_post_body(self):
        # ARRANGE
        request = FakeRequest(
            'POST', get={'query': 'from-get'}, post={'query': 'from-post'})

        # ACT
        self.view.search(request)

        # ASSERT
        self.doSearch.assert_called_once_with('from-get')

    def test_shows_an_empty_page_when_there_is_no_query(self):
        # ARRANGE
        request = FakeRequest('GET')

        # ACT
        self.view.search(request)

        # ASSERT
        self.doSearch.assert_not_called()
        context = self.render.call_args.args[2]
        self.assertEqual(context['query'], '')
        self.assertEqual(context['results'], [])

    def test_still_reads_the_query_from_the_url_path(self):
        # ARRANGE
        request = FakeRequest('GET')

        # ACT
        self.view.search(request, query='153.45 18.12')

        # ASSERT
        self.doSearch.assert_called_once_with('153.45 18.12')

    def test_json_checkbox_in_get_selects_the_json_branch(self):
        # ARRANGE
        request = FakeRequest('GET', get={'query': 'ZTF22aafxzfb', 'json': 'on'})
        # THE VIEW MODULE DOES NOT IMPORT json OR HttpResponse YET (SEPARATE KNOWN BUG)
        with mock.patch.object(self.view, 'json', create=True), \
                mock.patch.object(self.view, 'HttpResponse', create=True) as httpResponse:
            # ACT
            self.view.search(request)

        # ASSERT
        httpResponse.assert_called_once()
        self.render.assert_not_called()


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
