"""Unit tests for reading the search query from GET (bookmarkable) or POST (old callers)."""
import importlib
import json
import re
import sys
import types
import unittest
from datetime import datetime
from decimal import Decimal
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, '../../../../webserver')

from django.conf import settings as djangoSettings

# EACH TEST FILE MUST RUN IN ITS OWN PROCESS (AS JENKINS DOES) BECAUSE THEY CONFIGURE DJANGO DIFFERENTLY
if not djangoSettings.configured:
    djangoSettings.configure(DEBUG=False, SECRET_KEY='test')

import django.http

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
        'django.http': django.http,
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

    def test_json_checkbox_returns_a_json_response_of_the_results(self):
        # ARRANGE
        request = FakeRequest('GET', get={'query': 'ZTF22aafxzfb', 'json': 'on'})
        rows = [{
            'diaObjectId': 1234567890123456789, 'ra': 150.1,
            'last detected (days ago)': Decimal('1.25'),
            'firstSeen': datetime(2026, 1, 2, 3, 4, 5)}]
        self.favourites.suppress_hidden.return_value = (rows, {}, 0)

        # ACT
        response = self.view.search(request)

        # ASSERT
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(json.loads(response.content), [{
            'diaObjectId': 1234567890123456789, 'ra': 150.1,
            'last detected (days ago)': '1.25',
            'firstSeen': '2026-01-02T03:04:05'}])
        self.render.assert_not_called()

    def test_json_checkbox_returns_an_empty_list_when_nothing_matches(self):
        # ARRANGE
        request = FakeRequest('GET', get={'query': 'ZTF22aafxzfb', 'json': 'on'})
        self.favourites.suppress_hidden.return_value = ([], {}, 0)

        # ACT
        response = self.view.search(request)

        # ASSERT
        self.assertEqual(json.loads(response.content), [])


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

    def test_binds_an_object_id_as_an_integer_parameter(self):
        # ARRANGE
        objectId = '800436191404681043'

        # ACT
        self.view.do_search(objectId)

        # ASSERT
        calls = self.executed()
        self.assertEqual(len(calls), 3)
        self.assert_no_user_text_in_sql(objectId)
        self.assertEqual(calls[0][1], (800436191404681043,))
        self.assertEqual(calls[1][1], (99, objectId, objectId))
        self.assertEqual(calls[2][1], (800436191404681043,))
        for sql, params in calls:
            self.assertEqual(sql.count('%s'), len(params))

    def test_only_looks_up_the_object_id_columns_when_the_name_is_all_digits(self):
        # ACT
        self.view.do_search('ZTF21abc')

        # ASSERT
        calls = self.executed()
        self.assertEqual(len(calls), 1)
        self.assertIn('crossmatch_tns', calls[0][0])

    def test_binds_a_tns_name_with_its_prefix_stripped(self):
        # ACT
        self.view.do_search('AT2026abc')

        # ASSERT
        self.assert_no_user_text_in_sql('2026abc')
        tnsSql, tnsParams = self.executed()[0]
        self.assertEqual(tnsParams, (99, '2026abc', 'AT2026abc'))
        self.assertEqual(tnsSql.count('%s'), 3)

    def test_strips_a_spaced_tns_prefix_before_matching_the_name(self):
        # ACT
        self.view.do_search('SN 2026abc')

        # ASSERT
        self.assertEqual(self.executed()[0][1], (99, '2026abc', 'SN 2026abc'))

    def test_only_strips_the_prefix_not_letters_inside_a_name(self):
        # ACT
        self.view.do_search('ATLAS21xyz')

        # ASSERT
        self.assertEqual(self.executed()[0][1], (99, 'ATLAS21xyz', 'ATLAS21xyz'))

    def test_never_puts_injection_text_in_the_sql(self):
        for text in INJECTIONS:
            with self.subTest(text=text):
                self.cursor.execute.reset_mock()

                # ACT
                results, _ = self.view.do_search(text)

                # ASSERT
                self.assertEqual(results, [])
                self.assert_no_user_text_in_sql(text)

    def test_never_puts_hostile_object_names_in_the_sql(self):
        # ARRANGE
        hostileNames = ['ZTF21abc OR 1', 'a UNION SELECT 1', 'ZTF21abc--', 'x OR 1 OR 2']

        for text in hostileNames:
            with self.subTest(text=text):
                self.cursor.execute.reset_mock()

                # ACT
                self.view.do_search(text)

                # ASSERT
                calls = self.executed()
                self.assertTrue(calls)
                for sql, params in calls:
                    self.assertNotIn(text, sql)
                    self.assertIn(text, params)

    def test_never_puts_hostile_text_in_the_sql_even_if_the_allow_list_accepts_it(self):
        # ARRANGE
        acceptEverything = re.compile(r'.*', re.S)

        for text in INJECTIONS:
            with self.subTest(text=text), \
                    mock.patch.object(self.view, 'OBJECT_NAME', acceptEverything):
                self.cursor.execute.reset_mock()

                # ACT
                self.view.do_search(text)

                # ASSERT
                calls = self.executed()
                self.assertTrue(calls)
                for sql, params in calls:
                    self.assertNotIn(text, sql)
                    self.assertIn(text, params)

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

    def test_returns_nothing_when_the_cone_radius_is_not_a_number(self):
        # ACT
        results, schema = self.view.do_search('10:00:00 +02:00:00 abc')

        # ASSERT
        self.assertEqual((results, schema), ([], []))
        self.view.coneSearchHTM.assert_not_called()


OBJECT = 'object'
CONE = 'cone'
NOTHING = 'nothing'

ROUTING_CASES = [
    # OBJECT IDS
    ('800436191404681043', OBJECT),
    ('12345678901234567', OBJECT),
    ('1234567890123456789012', OBJECT),
    # TNS NAMES, WITH AND WITHOUT A PREFIX, IN ANY CASE
    ('2026abc', OBJECT),
    ('AT2026abc', OBJECT),
    ('SN2026abc', OBJECT),
    ('KN2026abc', OBJECT),
    ('AT 2026abc', OBJECT),
    ('SN 2026abc', OBJECT),
    ('at 2026abc', OBJECT),
    ('sn 2026abc', OBJECT),
    ('kn 2026abc', OBJECT),
    ('at2026abc', OBJECT),
    # INTERNAL DISCOVERY NAMES
    ('ZTF21abcdefg', OBJECT),
    ('ATLAS21xyz', OBJECT),
    ('Gaia21abc', OBJECT),
    ('PS1-13abc', OBJECT),
    ('ASASSN-21ab', OBJECT),
    ('CSS130101:123456+654321', OBJECT),
    # PARTIAL OR SHORT DISCOVERY NAMES
    ('21abc', OBJECT),
    ('123abc', OBJECT),
    # NAMES WITH A SINGLE INTERNAL SPACE
    ('Gaia 21abc', OBJECT),
    ('ZTF 21abc', OBJECT),
    ('abc def', OBJECT),
    # COORDINATES, PLAIN AND SEXAGESIMAL, WITH AND WITHOUT A RADIUS
    ('150.1 2.2', CONE),
    ('150.1,2.2', CONE),
    ('150.1|2.2', CONE),
    ('150.1 2.2 10', CONE),
    ('10:00:00 +02:00:00 5', CONE),
    ('10h00m00s +02d00m00s', CONE),
    ('10h00m00s +02d00m00s 5', CONE),
    # NEITHER A NAME NOR A CONE SEARCH
    ('12345', NOTHING),
    ('123456789012345678901234', NOTHING),
    ("a'b", NOTHING),
    ('a;b', NOTHING),
    ('', NOTHING),
]


class ObjectNameRoutingTest(unittest.TestCase):
    """Each query goes to the object branch, the cone branch, or nowhere."""

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

    def route_of(self, query):
        """Return the branch do_search took for this query."""
        self.view.do_search(query)
        if self.converter.ra_sexegesimal_to_decimal.called:
            return CONE
        if self.cursor.execute.called:
            return OBJECT
        return NOTHING

    def test_routes_every_query_to_the_expected_branch(self):
        for query, expected in ROUTING_CASES:
            with self.subTest(query=query):
                self.cursor.execute.reset_mock()
                self.converter.ra_sexegesimal_to_decimal.reset_mock()

                # ACT
                route = self.route_of(query)

                # ASSERT
                self.assertEqual(route, expected)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
