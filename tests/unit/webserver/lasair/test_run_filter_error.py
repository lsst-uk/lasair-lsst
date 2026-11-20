"""Tests that run_filter escapes the user's SQL and the database error in its error message.

The views pass this message to messages.error, and includes/messages.html renders
messages with |safe, so any unescaped text from the query would run as HTML.
"""
import context
import importlib.util
import os
import sys
import types
import unittest
from unittest import mock

HOSTILE_SQL = "select '<script>alert(1)</script>' from objects"
HOSTILE_DB_ERROR = "1064 (42000): near '<img src=x onerror=alert(2)>'"

UTILS_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../../webserver/lasair/apps/filter_query/utils.py'))


def _stub(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


def load_utils(cursor):
    """*load filter_query/utils.py with its heavy imports stubbed out*

    **Key Arguments:**

    - ``cursor`` -- the mock cursor that db_connect.readonly() hands back

    **Return:**

    - ``module`` -- the loaded utils module
    """
    connection = mock.MagicMock()
    connection.cursor.return_value = cursor
    stubs = {
        'lasair': _stub('lasair'),
        'lasair.query_builder': _stub('lasair.query_builder',
                                      check_query=lambda *a, **k: None,
                                      build_query=lambda *a, **k: HOSTILE_SQL),
        'src': _stub('src'),
        'src.db_connect': _stub('src.db_connect', readonly=lambda: connection),
        'src.topic_name': _stub('src.topic_name', topic_name=lambda *a: 'topic'),
        'lasair.apps': _stub('lasair.apps'),
        'lasair.apps.db_schema': _stub('lasair.apps.db_schema'),
        'lasair.apps.db_schema.utils': _stub('lasair.apps.db_schema.utils',
                                             get_schema=None, get_schema_dict=None,
                                             get_schema_for_query_selected=None),
        'lasair.utils': _stub('lasair.utils', datetime_converter=None),
        'confluent_kafka': _stub('confluent_kafka', admin=None, Producer=None),
        'lightcurves': _stub('lightcurves', lightcurve_fetcher=None),
        'util': _stub('util', lightcurve_lite=None),
    }
    with mock.patch.dict(sys.modules, stubs):
        spec = importlib.util.spec_from_file_location('filter_query_utils_under_test', UTILS_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class RunFilterErrorEscapingTest(unittest.TestCase):

    def setUp(self):
        # ARRANGE
        cursor = mock.MagicMock()
        cursor.execute.side_effect = Exception(HOSTILE_DB_ERROR)
        self.utils = load_utils(cursor)

    def run_failing_filter(self):
        return self.utils.run_filter(
            selected='objects.diaObjectId', tables='objects', conditions='1=1',
            limit=10, offset=0)[4]

    def test_escapes_the_users_sql(self):
        # ACT
        error = self.run_failing_filter()

        # ASSERT
        self.assertNotIn('<script>', error)
        self.assertIn('&lt;script&gt;', error)

    def test_escapes_the_database_error_text(self):
        # ACT
        error = self.run_failing_filter()

        # ASSERT
        self.assertNotIn('<img', error)
        self.assertIn('&lt;img src=x', error)

    def test_keeps_its_own_formatting_markup(self):
        # ACT
        error = self.run_failing_filter()

        # ASSERT
        self.assertTrue(error.startswith('Your query:<br/><b>'))
        self.assertIn('</b><br/>returned the error<br/><i>', error)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
