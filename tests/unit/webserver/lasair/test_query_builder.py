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
    def test_no_database_call_without_a_user(self, mock_remote):
        """An anonymous check returns before any permission query"""
        # ACT
        result = query_builder.check_query('diaObjectId', 'objects, annotator:tags_bob', '')

        # ASSERT
        self.assertIsNone(result)
        mock_remote.assert_not_called()


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
