"""Unit tests for the mark helpers that back every object result table."""
import unittest
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

from apps.favourites import utils


class FakeUser:
    def __init__(self, username, is_authenticated=True):
        self.username = username
        self.is_authenticated = is_authenticated


def row(diaObjectId, **extra):
    d = {'diaObjectId': diaObjectId}
    d.update(extra)
    return d


class MarksForTableTest(unittest.TestCase):
    """Tests for the marks_for_table helper."""

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_reads_the_marks_of_every_object_in_the_table(self, mock_marks):
        # ARRANGE
        mock_marks.return_value = {1: 'hidden', 2: 'favourite'}
        table = [row(1), row(2), row(3)]

        # ACT
        marks = utils.marks_for_table(FakeUser('dave'), table)

        # ASSERT
        mock_marks.assert_called_once_with('tags_dave', [1, 2, 3])
        self.assertEqual(marks, {1: 'hidden', 2: 'favourite'})

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_returns_no_marks_for_an_anonymous_viewer(self, mock_marks):
        # ARRANGE
        table = [row(1)]

        # ACT
        marks = utils.marks_for_table(FakeUser('', is_authenticated=False), table)

        # ASSERT
        self.assertEqual(marks, {})
        mock_marks.assert_not_called()

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_returns_no_marks_for_an_empty_table(self, mock_marks):
        # ACT
        marks = utils.marks_for_table(FakeUser('dave'), [])

        # ASSERT
        self.assertEqual(marks, {})
        mock_marks.assert_not_called()

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_returns_no_marks_when_no_row_carries_an_object_id(self, mock_marks):
        # ARRANGE
        table = [{'name': 'a'}, {'name': 'b'}]

        # ACT
        marks = utils.marks_for_table(FakeUser('dave'), table)

        # ASSERT
        self.assertEqual(marks, {})
        mock_marks.assert_not_called()


class SuppressHiddenTest(unittest.TestCase):
    """Tests for the suppress_hidden helper."""

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_removes_the_viewers_hidden_objects_from_the_table(self, mock_marks):
        # ARRANGE
        mock_marks.return_value = {1: 'hidden', 3: 'hidden'}
        table = [row(1), row(2), row(3), row(4)]

        # ACT
        kept, marks, omitted = utils.suppress_hidden(FakeUser('dave'), table)

        # ASSERT
        self.assertEqual([r['diaObjectId'] for r in kept], [2, 4])
        self.assertEqual(omitted, 2)
        self.assertEqual(marks, {1: 'hidden', 3: 'hidden'})

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_keeps_the_viewers_favourites(self, mock_marks):
        # ARRANGE
        mock_marks.return_value = {1: 'favourite', 2: 'hidden'}
        table = [row(1), row(2)]

        # ACT
        kept, marks, omitted = utils.suppress_hidden(FakeUser('dave'), table)

        # ASSERT
        self.assertEqual([r['diaObjectId'] for r in kept], [1])
        self.assertEqual(omitted, 1)

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_leaves_the_table_alone_when_the_viewer_holds_no_marks(self, mock_marks):
        # ARRANGE
        mock_marks.return_value = {}
        table = [row(1), row(2)]

        # ACT
        kept, marks, omitted = utils.suppress_hidden(FakeUser('dave'), table)

        # ASSERT
        self.assertIs(kept, table)
        self.assertEqual(marks, {})
        self.assertEqual(omitted, 0)

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_leaves_the_table_alone_for_an_anonymous_viewer(self, mock_marks):
        # ARRANGE
        table = [row(1)]

        # ACT
        kept, marks, omitted = utils.suppress_hidden(
            FakeUser('', is_authenticated=False), table)

        # ASSERT
        self.assertIs(kept, table)
        self.assertEqual(omitted, 0)
        mock_marks.assert_not_called()

    @mock.patch('apps.favourites.utils.annotate_util.marks_for_objects')
    def test_does_not_mutate_the_table_it_is_given(self, mock_marks):
        # ARRANGE
        mock_marks.return_value = {1: 'hidden'}
        table = [row(1), row(2)]

        # ACT
        kept, marks, omitted = utils.suppress_hidden(FakeUser('dave'), table)

        # ASSERT
        self.assertEqual(len(table), 2)
        self.assertIsNot(kept, table)


if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
