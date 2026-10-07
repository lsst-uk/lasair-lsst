import context
import query_builder
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock


def cursor_returning(rows):
    """Build a mock db_connect.remote() whose cursor iterates the given rows."""
    msl = MagicMock()
    cursor = MagicMock()
    cursor.__iter__.return_value = iter(rows)
    msl.cursor.return_value = cursor
    return msl, cursor


class CheckQueryAnnotatorPermissionTest(unittest.TestCase):
    """Tests for the annotator: permission branch of check_query."""

    @mock.patch('query_builder.db_connect.remote')
    def test_rejects_private_annotator_of_another_user(self, mock_remote):
        """A private annotator belonging to somebody else is refused"""
        # ARRANGE
        msl, cursor = cursor_returning([{'public': 0, 'user': 7}])
        mock_remote.return_value = msl

        # ACT / ASSERT
        with self.assertRaises(query_builder.QueryBuilderError):
            query_builder.check_query('diaObjectId', 'objects, annotator:tags_bob', '', user=3)

    @mock.patch('query_builder.db_connect.remote')
    def test_allows_own_private_annotator(self, mock_remote):
        """A user may query their own private annotator"""
        # ARRANGE
        msl, cursor = cursor_returning([{'public': 0, 'user': 3}])
        mock_remote.return_value = msl

        # ACT
        result = query_builder.check_query('diaObjectId', 'objects, annotator:tags_dave', '', user=3)

        # ASSERT
        self.assertIsNone(result)

    @mock.patch('query_builder.db_connect.remote')
    def test_allows_public_annotator_of_another_user(self, mock_remote):
        """A public annotator is available to everybody"""
        # ARRANGE
        msl, cursor = cursor_returning([{'public': 1, 'user': 7}])
        mock_remote.return_value = msl

        # ACT
        result = query_builder.check_query('diaObjectId', 'objects, annotator:sherlock', '', user=3)

        # ASSERT
        self.assertIsNone(result)

    @mock.patch('query_builder.db_connect.remote')
    def test_topic_is_parameterised(self, mock_remote):
        """The annotator topic is passed as a query parameter, never interpolated"""
        # ARRANGE
        msl, cursor = cursor_returning([{'public': 1, 'user': 7}])
        mock_remote.return_value = msl

        # ACT
        query_builder.check_query('diaObjectId', 'objects, annotator:sherlock', '', user=3)

        # ASSERT
        args = cursor.execute.call_args[0]
        self.assertEqual(len(args), 2)
        self.assertNotIn('sherlock', args[0])
        self.assertEqual(args[1], ('sherlock',))

    @mock.patch('query_builder.db_connect.remote')
    def test_checks_every_topic_of_a_multi_annotator_from(self, mock_remote):
        """Each topic of the &-joined web form is checked"""
        # ARRANGE
        msl, cursor = cursor_returning([{'public': 1, 'user': 7}, {'public': 1, 'user': 7}])
        mock_remote.return_value = msl

        # ACT
        query_builder.check_query('diaObjectId', 'objects, annotator:sherlock&tags_bob', '', user=3)

        # ASSERT
        topics = [call[0][1][0] for call in cursor.execute.call_args_list]
        self.assertEqual(topics, ['sherlock', 'tags_bob'])

    @mock.patch('query_builder.db_connect.remote')
    def test_an_annotator_prefix_without_a_colon_is_still_checked(self, mock_remote):
        """build_query joins on any token starting 'annotator', so the check must too"""
        # ARRANGE
        msl, cursor = cursor_returning([{'public': 0, 'user': 7}])
        mock_remote.return_value = msl

        # ACT / ASSERT
        with self.assertRaises(query_builder.QueryBuilderError):
            query_builder.check_query(
                'diaObjectId', 'objects, annotators:tags_bob', '', user=3)

    def test_build_query_refuses_a_malformed_annotator_fragment(self):
        """A fragment the permission check cannot parse must not build a join"""
        with self.assertRaises(query_builder.QueryBuilderError):
            query_builder.build_query('diaObjectId', 'objects, annotatortags_bob', '')

    @mock.patch('query_builder.db_connect.remote')
    def test_no_database_call_without_a_user(self, mock_remote):
        """An anonymous check returns before any permission query"""
        # ACT
        result = query_builder.check_query('diaObjectId', 'objects, annotator:tags_bob', '')

        # ASSERT
        self.assertIsNone(result)
        mock_remote.assert_not_called()


class CheckQueryMarkFragmentsTest(unittest.TestCase):
    """check_query must know the two mark fragments by name."""

    @mock.patch('query_builder.db_connect.remote')
    def test_the_mark_fragments_are_accepted(self, mock_remote):
        """A filter carrying both fragments passes validation"""
        # ACT
        result = query_builder.check_query(
            'diaObjectId', 'objects, favourite:only, hidden:include', '', user=3)

        # ASSERT
        self.assertIsNone(result)
        mock_remote.assert_not_called()

    @mock.patch('query_builder.db_connect.remote')
    def test_a_misspelled_mark_fragment_is_rejected(self, mock_remote):
        """An unrecognised favourites fragment would otherwise be silently ignored"""
        with self.assertRaises(query_builder.QueryBuilderError):
            query_builder.check_query(
                'diaObjectId', 'objects, favourite:all', '', user=3)

    @mock.patch('query_builder.db_connect.remote')
    def test_a_misspelled_hidden_fragment_is_rejected(self, mock_remote):
        with self.assertRaises(query_builder.QueryBuilderError):
            query_builder.check_query(
                'diaObjectId', 'objects, hidden:yes', '', user=3)


class BuildQueryMarkPredicatesTest(unittest.TestCase):
    """Tests for the hidden exclusion and the favourites restriction."""

    HIDDEN_EXCLUSION = (
        "NOT EXISTS (SELECT 1 FROM annotations "
        "WHERE annotations.diaObjectId = objects.diaObjectId "
        "AND annotations.topic = 'tags_dave' "
        "AND annotations.classification = 'hidden')")

    FAVOURITE_RESTRICTION = (
        "EXISTS (SELECT 1 FROM annotations "
        "WHERE annotations.diaObjectId = objects.diaObjectId "
        "AND annotations.topic = 'tags_dave' "
        "AND annotations.classification = 'favourite')")

    def test_hidden_is_excluded_for_an_owner(self):
        """The exclusion is emitted for an owner who has not opted out"""
        # ACT
        sql = query_builder.build_query('diaObjectId', 'objects', 'ra > 1', owner_topic='tags_dave')

        # ASSERT
        self.assertIn(self.HIDDEN_EXCLUSION, sql)

    def test_no_exclusion_without_an_owner_topic(self):
        """An ad-hoc query with no owner excludes nothing"""
        # ACT
        sql = query_builder.build_query('diaObjectId', 'objects', 'ra > 1')

        # ASSERT
        self.assertNotIn('NOT EXISTS', sql)

    def test_include_hidden_suppresses_the_exclusion(self):
        """The hidden:include fragment turns the exclusion off"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, hidden:include', 'ra > 1', owner_topic='tags_dave')

        # ASSERT
        self.assertNotIn('NOT EXISTS', sql)

    def test_exclude_hidden_false_suppresses_the_exclusion(self):
        """A non-owner running a public filter gets no hidden exclusion"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only', 'ra > 1',
            owner_topic='tags_dave', exclude_hidden=False)

        # ASSERT
        self.assertNotIn('NOT EXISTS', sql)
        self.assertIn(self.FAVOURITE_RESTRICTION, sql)

    def test_favourites_only_is_emitted(self):
        """The favourite:only fragment restricts to the owner's favourites"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only', 'ra > 1', owner_topic='tags_dave')

        # ASSERT
        self.assertIn(self.FAVOURITE_RESTRICTION, sql)

    def test_both_predicates_may_be_emitted_together(self):
        """Both boxes ticked emits both predicates; the rows can coexist"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only, hidden:include', 'ra > 1',
            owner_topic='tags_dave')

        # ASSERT
        self.assertIn(self.FAVOURITE_RESTRICTION, sql)
        self.assertNotIn('NOT EXISTS', sql)

    def test_the_fragments_are_not_treated_as_tables(self):
        """Neither fragment reaches the FROM list"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only, hidden:include', '', owner_topic='tags_dave')

        # ASSERT
        from_clause = sql.split('FROM')[1].split('WHERE')[0]
        self.assertNotIn('favourite', from_clause)
        self.assertNotIn('hidden', from_clause)

    def test_favourites_only_without_an_owner_is_an_error(self):
        """There is no owner whose favourites could be meant"""
        with self.assertRaises(query_builder.QueryBuilderError):
            query_builder.build_query('diaObjectId', 'objects, favourite:only', '')

    def test_the_exclusion_survives_an_order_by_only_condition(self):
        """A condition that is only an ORDER BY still gets the exclusion"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects', 'ORDER BY ra', owner_topic='tags_dave')

        # ASSERT
        self.assertIn(self.HIDDEN_EXCLUSION, sql)
        self.assertTrue(sql.rstrip().endswith('ORDER BY ra'))


class BuildQueryForDisplayTest(unittest.TestCase):
    """Tests for the for_display placeholder path: what a user sees must
    never contain the mark predicates' EXISTS block, and the SQL built
    without for_display must stay byte-for-byte the same as before."""

    HIDDEN_EXCLUSION = (
        "NOT EXISTS (SELECT 1 FROM annotations "
        "WHERE annotations.diaObjectId = objects.diaObjectId "
        "AND annotations.topic = 'tags_dave' "
        "AND annotations.classification = 'hidden')")

    FAVOURITE_RESTRICTION = (
        "EXISTS (SELECT 1 FROM annotations "
        "WHERE annotations.diaObjectId = objects.diaObjectId "
        "AND annotations.topic = 'tags_dave' "
        "AND annotations.classification = 'favourite')")

    def test_without_display_mode_the_real_sql_is_unchanged(self):
        """Regression: the default call still emits the exact current EXISTS SQL"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only', 'ra > 1', owner_topic='tags_dave')

        # ASSERT
        self.assertIn(self.HIDDEN_EXCLUSION, sql)
        self.assertIn(self.FAVOURITE_RESTRICTION, sql)

    def test_without_display_mode_the_whole_sql_string_is_byte_for_byte_unchanged(self):
        """The exact frozen string this build produces, not just substrings of it.

        This is what a caller writes into myqueries.real_sql and what the
        Kafka filter pipeline later runs verbatim, so predicate order and
        surrounding whitespace matter just as much as the predicates."""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only', 'ra > 1', owner_topic='tags_dave')

        # ASSERT
        self.assertEqual(
            sql,
            'SELECT diaObjectId \n'
            'FROM objects \n'
            'WHERE\n '
            + self.FAVOURITE_RESTRICTION + ' AND\n '
            + self.HIDDEN_EXCLUSION + ' AND\n '
            'ra > 1')

    def test_a_non_owner_gets_no_hidden_placeholder_in_display_mode_either(self):
        """build_query_for_filter(is_owner=False) sets exclude_hidden=False;
        the display path must honour that exactly as the real path does"""
        # ACT
        sql = query_builder.build_query_for_filter(
            {'selected': 'objects.diaObjectId', 'tables': 'objects',
             'conditions': 'ra > 1', 'username': 'dave'},
            is_owner=False, for_display=True)

        # ASSERT
        self.assertNotIn(query_builder.MARK_DISPLAY_PLACEHOLDER['hidden'], sql)
        self.assertNotIn('annotations', sql)

    def test_display_mode_emits_the_favourite_placeholder(self):
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only', 'ra > 1',
            owner_topic='tags_dave', for_display=True)

        # ASSERT
        self.assertIn(query_builder.MARK_DISPLAY_PLACEHOLDER['favourite'], sql)
        self.assertNotIn(self.FAVOURITE_RESTRICTION, sql)

    def test_display_mode_emits_the_hidden_placeholder_by_default(self):
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects', 'ra > 1', owner_topic='tags_dave', for_display=True)

        # ASSERT
        self.assertIn(query_builder.MARK_DISPLAY_PLACEHOLDER['hidden'], sql)
        self.assertNotIn(self.HIDDEN_EXCLUSION, sql)

    def test_display_mode_hides_the_hidden_placeholder_with_hidden_include(self):
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, hidden:include', 'ra > 1',
            owner_topic='tags_dave', for_display=True)

        # ASSERT
        self.assertNotIn(query_builder.MARK_DISPLAY_PLACEHOLDER['hidden'], sql)

    def test_display_mode_hides_the_hidden_placeholder_with_exclude_hidden_false(self):
        """A non-owner viewing a public filter gets no hidden placeholder either"""
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects', 'ra > 1',
            owner_topic='tags_dave', exclude_hidden=False, for_display=True)

        # ASSERT
        self.assertNotIn(query_builder.MARK_DISPLAY_PLACEHOLDER['hidden'], sql)

    def test_display_mode_output_never_leaks_annotations_or_the_topic(self):
        # ACT
        sql = query_builder.build_query(
            'diaObjectId', 'objects, favourite:only', 'ra > 1',
            owner_topic='tags_dave', for_display=True)

        # ASSERT
        self.assertNotIn('annotations', sql)
        self.assertNotIn('tags_dave', sql)

    def test_build_query_for_filter_passes_display_mode_through(self):
        # ACT
        sql = query_builder.build_query_for_filter(
            {'selected': 'objects.diaObjectId', 'tables': 'objects',
             'conditions': 'ra > 1', 'username': 'dave'},
            is_owner=True, for_display=True)

        # ASSERT
        self.assertIn(query_builder.MARK_DISPLAY_PLACEHOLDER['hidden'], sql)
        self.assertNotIn('annotations', sql)


class BuildQueryForFilterTest(unittest.TestCase):
    """Tests for the single door saved filters build their SQL through."""

    def setUp(self):
        self.row = {
            'selected': 'objects.diaObjectId',
            'tables': 'objects',
            'conditions': 'ra > 1',
            'username': 'dave',
        }

    def test_the_owner_gets_their_own_hidden_exclusion(self):
        # ACT
        sql = query_builder.build_query_for_filter(self.row, is_owner=True)

        # ASSERT
        self.assertIn("annotations.topic = 'tags_dave'", sql)
        self.assertIn('NOT EXISTS', sql)

    def test_a_non_owner_gets_no_hidden_exclusion(self):
        # ACT
        sql = query_builder.build_query_for_filter(self.row, is_owner=False)

        # ASSERT
        self.assertNotIn('NOT EXISTS', sql)

    def test_a_non_owner_still_gets_the_owners_favourites(self):
        # ARRANGE
        self.row['tables'] = 'objects, favourite:only'

        # ACT
        sql = query_builder.build_query_for_filter(self.row, is_owner=False)

        # ASSERT
        self.assertIn("annotations.classification = 'favourite'", sql)
        self.assertIn("annotations.topic = 'tags_dave'", sql)

    def test_include_hidden_is_honoured_for_the_owner(self):
        # ARRANGE
        self.row['tables'] = 'objects, hidden:include'

        # ACT
        sql = query_builder.build_query_for_filter(self.row, is_owner=True)

        # ASSERT
        self.assertNotIn('NOT EXISTS', sql)

    def test_a_model_instance_is_accepted_as_well_as_a_dict(self):
        """Callers pass a filter_query model instance or a database row"""
        # ARRANGE
        class Owner:
            username = 'dave'

        class FilterQueryRow:
            selected = 'objects.diaObjectId'
            tables = 'objects'
            conditions = 'ra > 1'
            user = Owner()

        row = FilterQueryRow()

        # ACT
        sql = query_builder.build_query_for_filter(row, is_owner=True)

        # ASSERT
        self.assertIn("annotations.topic = 'tags_dave'", sql)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
