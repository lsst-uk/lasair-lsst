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


INJECTIONS = [
    "a'OR/**/1=1#",
    "1' OR '1'='1",
    "x'; DROP TABLE objects;--",
    'a" or ""="',
]


class DoSearchSqlTest(unittest.TestCase):
    """Every user-derived value must reach MySQL as a bound parameter, never as SQL text."""

    def setUp(self):
        self.view, _, _ = load_view()
        self.cursor = mock.MagicMock()
        self.cursor.fetchall.return_value = []
        remotePatch = mock.patch.object(self.view.db_connect, 'remote')
        remote = remotePatch.start()
        self.addCleanup(remotePatch.stop)
        remote.return_value.cursor.return_value = self.cursor
        converter = self.view.unit_conversion.return_value
        converter.ra_sexegesimal_to_decimal.return_value = 150.1
        converter.dec_sexegesimal_to_decimal.return_value = 2.2
        self.view.coneSearchHTM.return_value = ('found', [])

    def executed(self):
        """Return the (sql, params) of every execute call."""
        return [
            (call.args[0], call.args[1] if len(call.args) > 1 else None)
            for call in self.cursor.execute.call_args_list]

    def assert_no_user_text_in_sql(self, text):
        for sql, _ in self.executed():
            self.assertNotIn(text, sql)

    def test_binds_an_object_id_as_a_parameter(self):
        # ARRANGE
        objectId = '800436191404681043'

        # ACT
        self.view.do_search(objectId)

        # ASSERT
        calls = self.executed()
        self.assertEqual(len(calls), 3)
        self.assert_no_user_text_in_sql(objectId)
        for sql, params in calls:
            self.assertIn(objectId, params)
            self.assertEqual(sql.count('%s'), len(params))

    def test_binds_a_tns_name_with_its_prefix_stripped(self):
        # ACT
        self.view.do_search('AT2026abc')

        # ASSERT
        self.assert_no_user_text_in_sql('2026abc')
        tnsSql, tnsParams = self.executed()[1]
        self.assertEqual(tnsParams, (99, '2026abc', 'AT2026abc'))
        self.assertEqual(tnsSql.count('%s'), 3)

    def test_strips_a_spaced_tns_prefix_before_matching_the_name(self):
        # ACT
        self.view.do_search('SN 2026abc')

        # ASSERT
        self.assertEqual(self.executed()[1][1], (99, '2026abc', 'SN 2026abc'))

    def test_only_strips_the_prefix_not_letters_inside_a_name(self):
        # ACT
        self.view.do_search('ATLAS21xyz')

        # ASSERT
        self.assertEqual(self.executed()[1][1], (99, 'ATLAS21xyz', 'ATLAS21xyz'))

    def test_never_puts_injection_text_in_the_sql(self):
        for text in INJECTIONS:
            with self.subTest(text=text):
                self.cursor.execute.reset_mock()

                # ACT
                results, _ = self.view.do_search(text)

                # ASSERT
                self.assertEqual(results, [])
                self.assert_no_user_text_in_sql(text)

    def test_binds_the_cone_search_ids_as_integers_with_one_placeholder_each(self):
        # ARRANGE
        self.view.coneSearchHTM.return_value = ('found', [
            (0.1, {'diaObjectId': 800436191404681043}),
            (0.2, {'diaObjectId': '808513610424051231'})])

        # ACT
        self.view.do_search('150.1 2.2')

        # ASSERT
        sql, params = self.executed()[0]
        self.assertIn('in (%s,%s)', sql)
        self.assertEqual(params, (800436191404681043, 808513610424051231))

    def test_runs_no_query_when_the_cone_search_finds_nothing(self):
        # ACT
        results, _ = self.view.do_search('150.1 2.2')

        # ASSERT
        self.assertEqual(results, [])
        self.cursor.execute.assert_not_called()


class ObjectNameAllowListTest(unittest.TestCase):
    """Which queries are object names and which fall through to the cone search."""

    def setUp(self):
        self.view, _, _ = load_view()
        self.cursor = mock.MagicMock()
        self.cursor.fetchall.return_value = []
        remotePatch = mock.patch.object(self.view.db_connect, 'remote')
        remote = remotePatch.start()
        self.addCleanup(remotePatch.stop)
        remote.return_value.cursor.return_value = self.cursor
        self.converter = self.view.unit_conversion.return_value
        self.converter.ra_sexegesimal_to_decimal.return_value = 150.1
        self.converter.dec_sexegesimal_to_decimal.return_value = 2.2
        self.view.coneSearchHTM.return_value = ('found', [])

    def test_treats_real_object_names_as_names(self):
        names = [
            '800436191404681043', '12345678901234567', '1234567890123456789012',
            '2026abc', 'AT2026abc', 'SN2026abc', 'KN2026abc', 'AT 2026abc',
            'SN 2026abc', 'ZTF21abcdefg', 'ATLAS21xyz', 'Gaia21abc', 'PS1-13abc',
            'ASASSN-21ab', 'CSS130101:123456+654321']
        for name in names:
            with self.subTest(name=name):
                self.cursor.execute.reset_mock()
                self.view.coneSearchHTM.reset_mock()

                # ACT
                self.view.do_search(name)

                # ASSERT
                self.assertEqual(self.cursor.execute.call_count, 3)
                self.view.coneSearchHTM.assert_not_called()

    def test_sends_coordinates_to_the_cone_search_with_the_default_radius(self):
        for query in ['150.1 2.2', '150.1,2.2', '150.1|2.2']:
            with self.subTest(query=query):
                self.view.coneSearchHTM.reset_mock()

                # ACT
                self.view.do_search(query)

                # ASSERT
                self.assertEqual(
                    self.view.coneSearchHTM.call_args.args[:3], (150.1, 2.2, 5.))

    def test_sends_sexagesimal_coordinates_and_radius_to_the_cone_search(self):
        # ACT
        self.view.do_search('10:00:00 +02:00:00 7')

        # ASSERT
        self.converter.ra_sexegesimal_to_decimal.assert_called_once_with(ra='10:00:00')
        self.converter.dec_sexegesimal_to_decimal.assert_called_once_with(dec='+02:00:00')
        self.assertEqual(self.view.coneSearchHTM.call_args.args[:3], (150.1, 2.2, 7.))

    def test_does_not_treat_other_text_as_an_object_name(self):
        queries = ['12345', '123456789012345678901234', "a'b", 'abc def', 'a;b', '']
        for query in queries:
            with self.subTest(query=query):
                self.cursor.execute.reset_mock()
                self.converter.ra_sexegesimal_to_decimal.side_effect = ValueError

                # ACT
                results, schema = self.view.do_search(query)

                # ASSERT
                self.assertEqual((results, schema), ([], []))
                self.cursor.execute.assert_not_called()

    def test_returns_nothing_when_the_cone_radius_is_not_a_number(self):
        # ACT
        results, schema = self.view.do_search('10:00:00 +02:00:00 abc')

        # ASSERT
        self.assertEqual((results, schema), ([], []))
        self.view.coneSearchHTM.assert_not_called()


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
