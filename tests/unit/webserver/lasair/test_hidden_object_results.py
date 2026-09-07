"""Focused view tests for showing a viewer's hidden result objects."""
import importlib
import sys
import types
import unittest
from pathlib import Path
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, '../../../../webserver')


class FakeForm:
    def __init__(self, *args, **kwargs):
        pass


class FakeCursor:
    def __init__(self, table):
        self.table = table

    def execute(self, *args, **kwargs):
        pass

    def fetchall(self):
        return self.table

    def __iter__(self):
        return iter([{'count': 1}])


class FakeRequest:
    def __init__(self, user, show_hidden=False):
        self.user = user
        self.GET = {'show_hidden': '1'} if show_hidden else {}
        self.POST = {}
        self.method = 'GET'


class FakeUser:
    def __init__(self, is_authenticated=True):
        self.id = 1
        self.username = 'dave'
        self.is_authenticated = is_authenticated
        self.is_superuser = False


def module(**attributes):
    result = types.ModuleType('stub')
    result.__dict__.update(attributes)
    return result


def load_view(kind):
    """Load one detail view with framework and infrastructure edges stubbed."""
    csrf_exempt = lambda function: function
    login_required = lambda function: function
    render = mock.Mock(side_effect=lambda request, template, context: context)
    settings = SimpleNamespace(DEBUG=False, WATCHLIST_MAX_CROSSMATCH=1000)
    messages = module(error=mock.Mock(), info=mock.Mock(), success=mock.Mock())
    db_connect = module(remote=mock.Mock())
    favourites_utils = module(
        suppress_hidden=mock.Mock(), marks_for_table=mock.Mock())
    forms = module(
        WatchlistForm=FakeForm, UpdateWatchlistForm=FakeForm,
        DuplicateWatchlistForm=FakeForm, WatchmapForm=FakeForm,
        UpdateWatchmapForm=FakeForm, DuplicateWatchmapForm=FakeForm)
    models = module(Watchlist=object, WatchlistCone=object, Watchmap=object)
    modules = {
        'django': module(),
        'django.contrib': module(messages=messages),
        'django.contrib.messages': messages,
        'django.contrib.auth': module(),
        'django.contrib.auth.decorators': module(login_required=login_required),
        'django.contrib.auth.models': module(User=object),
        'django.views': module(),
        'django.views.decorators': module(),
        'django.views.decorators.csrf': module(csrf_exempt=csrf_exempt),
        'django.template': module(),
        'django.template.context_processors': module(csrf=lambda request: {}),
        'django.http': module(HttpResponse=object, HttpResponseRedirect=object, FileResponse=object),
        'django.shortcuts': module(
            render=render, get_object_or_404=mock.Mock(), redirect=mock.Mock()),
        'django.conf': module(settings=settings),
        'django.utils': module(),
        'django.utils.text': module(slugify=lambda value: value),
        'src.db_connect': db_connect,
        'src.run_crossmatch_optimised': module(run_crossmatch=mock.Mock()),
        'src.bad_fits': module(),
        'lasair.apps.favourites.utils': favourites_utils,
        'lasair.apps.db_schema.utils': module(get_schema_dict=mock.Mock(return_value={'name': 'name', 'arcsec': 'arcsec'})),
        f'lasair.apps.{kind}.forms': forms,
        f'lasair.apps.{kind}.models': models,
        'lasair.apps.watchlist.utils': module(
            handle_uploaded_file=mock.Mock(), add_watchlist_metadata=mock.Mock()),
        'lasair.apps.watchmap.utils': module(
            make_image_of_MOC=mock.Mock(), add_watchmap_metadata=mock.Mock()),
        'lasair.utils': module(bytes2string=mock.Mock(), string2bytes=mock.Mock()),
        'matplotlib': module(pyplot=module()),
        'matplotlib.pyplot': module(),
        'astropy': module(units=module(), coordinates=module()),
        'astropy.units': module(),
        'astropy.coordinates': module(Angle=object, SkyCoord=object),
    }
    view_name = f'lasair.apps.{kind}.views'
    with mock.patch.dict(sys.modules, modules):
        sys.modules.pop(view_name, None)
        view = importlib.import_module(view_name)
    return view, render, db_connect, favourites_utils


class HiddenObjectResultsTest(unittest.TestCase):
    TABLE = [{'diaObjectId': 10}, {'diaObjectId': 20}]
    MARKS = {10: 'hidden', 20: 'favourite'}

    def _detail_context(self, kind, user, show_hidden):
        view, render, db_connect, favourites_utils = load_view(kind)
        cursor = FakeCursor(self.TABLE)
        db_connect.remote.return_value.cursor.return_value = cursor
        resource = SimpleNamespace(user=SimpleNamespace(id=1), public=True)
        view.get_object_or_404.return_value = resource
        favourites_utils.suppress_hidden.return_value = (
            [self.TABLE[1]], self.MARKS, 1)
        favourites_utils.marks_for_table.return_value = self.MARKS
        request = FakeRequest(user, show_hidden=show_hidden)
        detail = getattr(view, f'{kind}_detail')
        detail(request, 4)
        return render.call_args.args[2], favourites_utils

    def test_watchlist_show_hidden_keeps_rows_and_marks_them(self):
        # ARRANGE / ACT
        context, favourites_utils = self._detail_context(
            'watchlist', FakeUser(), show_hidden=True)

        # ASSERT
        self.assertEqual(context['table'], self.TABLE)
        self.assertEqual(context['marks'], self.MARKS)
        self.assertEqual(context['hidden_omitted'], 0)
        self.assertTrue(context['show_hidden_now'])
        favourites_utils.suppress_hidden.assert_not_called()
        favourites_utils.marks_for_table.assert_called_once_with(mock.ANY, self.TABLE)

    def test_watchmap_show_hidden_keeps_rows_and_marks_them(self):
        # ARRANGE / ACT
        context, favourites_utils = self._detail_context(
            'watchmap', FakeUser(), show_hidden=True)

        # ASSERT
        self.assertEqual(context['table'], self.TABLE)
        self.assertEqual(context['marks'], self.MARKS)
        self.assertEqual(context['hidden_omitted'], 0)
        self.assertTrue(context['show_hidden_now'])
        favourites_utils.suppress_hidden.assert_not_called()
        favourites_utils.marks_for_table.assert_called_once_with(mock.ANY, self.TABLE)

    def test_default_view_suppresses_hidden_rows_and_reports_omission(self):
        # ARRANGE / ACT
        context, favourites_utils = self._detail_context(
            'watchlist', FakeUser(), show_hidden=False)

        # ASSERT
        self.assertEqual(context['table'], [self.TABLE[1]])
        self.assertEqual(context['hidden_omitted'], 1)
        self.assertFalse(context['show_hidden_now'])
        favourites_utils.suppress_hidden.assert_called_once_with(mock.ANY, self.TABLE)

    def test_all_hidden_watchmap_results_keep_the_omission_count_for_the_reveal_link(self):
        # ARRANGE
        view, render, db_connect, favourites_utils = load_view('watchmap')
        db_connect.remote.return_value.cursor.return_value = FakeCursor(self.TABLE)
        view.get_object_or_404.return_value = SimpleNamespace(
            user=SimpleNamespace(id=1), public=True)
        favourites_utils.suppress_hidden.return_value = ([], self.MARKS, 2)

        # ACT
        view.watchmap_detail(FakeRequest(FakeUser()), 4)
        context = render.call_args.args[2]

        # ASSERT
        self.assertEqual(context['table'], [])
        self.assertEqual(context['hidden_omitted'], 2)

    def test_no_hidden_rows_reports_no_omission(self):
        # ARRANGE
        view, render, db_connect, favourites_utils = load_view('watchlist')
        db_connect.remote.return_value.cursor.return_value = FakeCursor(self.TABLE)
        view.get_object_or_404.return_value = SimpleNamespace(
            user=SimpleNamespace(id=1), public=True)
        favourites_utils.suppress_hidden.return_value = (self.TABLE, {}, 0)

        # ACT
        view.watchlist_detail(FakeRequest(FakeUser()), 4)
        context = render.call_args.args[2]

        # ASSERT
        self.assertEqual(context['hidden_omitted'], 0)

    def test_anonymous_show_hidden_request_does_not_bypass_suppression(self):
        # ARRANGE / ACT
        context, favourites_utils = self._detail_context(
            'watchmap', FakeUser(is_authenticated=False), show_hidden=True)

        # ASSERT
        self.assertEqual(context['table'], [self.TABLE[1]])
        self.assertFalse(context['show_hidden_now'])
        favourites_utils.suppress_hidden.assert_called_once_with(mock.ANY, self.TABLE)


class ObjectListWidgetTest(unittest.TestCase):
    """The shared result widget must retain its hidden-object affordances."""

    def test_renders_the_hidden_result_state_only_when_its_context_requires_it(self):
        # ARRANGE
        widget = (Path(__file__).resolve().parents[4] / 'webserver' / 'lasair'
                  / 'templates' / 'includes' / 'widgets'
                  / 'widget_objectlist_table.html').read_text()

        # ASSERT
        self.assertIn('{% if table|length > 0 or hidden_omitted %}', widget)
        self.assertIn('{% if hidden_omitted %}', widget)
        self.assertIn('<a href="?show_hidden=1">show them</a>.', widget)
        self.assertIn('Showing your hidden objects for this page.', widget)


if __name__ == '__main__':
    unittest.main()
