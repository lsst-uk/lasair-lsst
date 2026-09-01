import context
import annotate_util
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock


class AnnotateUtilTest(unittest.TestCase):
    """Tests for annotation utils."""

    @mock.patch('annotate_util.Producer')
    def test_insert_annotation_kafka(self, mock_producer):
        """Test insert_annotation_kafka function"""
        annotate_util.lasair_settings.ANNOTATION_TOPIC = 'asdf'
        annotate_util.insert_annotation_kafka(123, 'test_topic', 'test_class', 'v1', 'expl', '{}', 'test_url')
        mock_producer.return_value.produce.assert_called_once_with(
            'asdf',
            '{"diaObjectId": 123, "topic": "test_topic", "classification": "test_class", "version": "v1", '
            '"explanation": "expl", "classdict": "{}", "url": "test_url"}'
            )
        mock_producer.return_value.flush.assert_called_once()

    def test_insert_annotations_kafka(self):
        """Test insert_annotations_kafka function"""
        # not required as tested by above
        pass

    @mock.patch('db_connect.remote')
    def test_insert_annotation_db(self, mock_db):
        """Test insert_annotation_db function"""
        # ARRANGE
        mock_msl = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_msl
        mock_msl.cursor.return_value = mock_cursor

        # ACT
        annotate_util.insert_annotation_db(123, 'test_topic', 'test_class', 'v1', 'expl', '{}', 'test_url')

        # ASSERT
        expected_delete = 'DELETE FROM annotations WHERE diaObjectId=%s AND topic=%s'
        expected_insert = (
            'INSERT INTO annotations ('
            'diaObjectId, topic, version, classification, explanation, classdict, url'
            ') VALUES (%s, %s, %s, %s, %s, %s, %s)'
        )
        mock_cursor.execute.assert_any_call(expected_delete, (123, 'test_topic'))
        mock_cursor.execute.assert_any_call(
            expected_insert,
            (123, 'test_topic', 'v1', 'test_class', 'expl', '{}', 'test_url'))

    @mock.patch('db_connect.remote')
    def test_insert_annotation_db_tags(self, mock_db):
        """Test insert_annotation_db deletes only the matching tag on a tags topic"""
        # ARRANGE
        mock_msl = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_msl
        mock_msl.cursor.return_value = mock_cursor

        # ACT
        annotate_util.insert_annotation_db(123, 'tags_test_topic', 'test_class')

        # ASSERT
        expected_delete = (
            'DELETE FROM annotations WHERE diaObjectId=%s AND topic=%s '
            'AND classification=%s'
        )
        mock_cursor.execute.assert_any_call(
            expected_delete, (123, 'tags_test_topic', 'test_class'))

    @mock.patch('db_connect.remote')
    def test_delete_annotation(self, mock_db):
        """Test delete_annotation function"""
        # ACT
        annotate_util.delete_annotation(123, 'test_topic', 'test_class')

        # ASSERT
        expected_delete = 'DELETE FROM annotations WHERE diaObjectId=%s AND topic=%s'
        mock_db.return_value.cursor.return_value.execute.assert_called_with(
            expected_delete, (123, 'test_topic'))

    @mock.patch('annotate_util.db_connect.remote')
    def test_delete_annotation_tags(self, mock_db):
        """Test delete_annotation function for tags"""
        # ACT
        annotate_util.delete_annotation(123, 'tags_test_topic', 'test_class')

        # ASSERT
        expected_delete = (
            'DELETE FROM annotations WHERE diaObjectId=%s AND topic=%s '
            'AND classification=%s'
        )
        mock_db.return_value.cursor.return_value.execute.assert_called_with(
            expected_delete, (123, 'tags_test_topic', 'test_class'))

    @mock.patch('annotate_util.db_connect.remote')
    def test_delete_annotation_error(self, mock_db):
        """Test that delete_annotation function raises exception if called without classification on a tags topic"""
        with self.assertRaises(annotate_util.AnnotationError):
            annotate_util.delete_annotation(123, 'tags_test_topic')

    @mock.patch('annotate_util.db_connect.remote')
    def test_classifications_for_object(self, mock_db):
        """Test classifications_for_object function"""
        # ACT
        annotate_util.classifications_for_object('test_topic', 123)

        # ASSERT
        expected_select = (
            'SELECT classification FROM annotations '
            'WHERE topic=%s AND diaObjectId=%s'
            )
        mock_db.return_value.cursor.return_value.execute.assert_called_with(
            expected_select, ('test_topic', 123))

    @mock.patch('annotate_util.db_connect.remote')
    def test_objects_for_classification(self, mock_db):
        """Test objects_for_classification function"""
        # ACT
        annotate_util.objects_for_classification('test_topic', 'apple')

        # ASSERT
        expected_select = (
            'SELECT diaObjectId FROM annotations '
            'WHERE topic=%s AND classification=%s'
            )
        mock_db.return_value.cursor.return_value.execute.assert_called_with(
            expected_select, ('test_topic', 'apple'))


class MarkObjectTest(unittest.TestCase):
    """Tests for the mark_object service function."""

    def setUp(self):
        self.user = MagicMock()
        self.user.username = 'dave'
        self.user.id = 3

    @mock.patch('annotate_util.make_tag_annotator.make_annotator')
    @mock.patch('annotate_util.delete_annotation')
    @mock.patch('annotate_util.insert_annotation_db')
    @mock.patch('annotate_util.db_connect.remote')
    def test_favourite_displaces_hidden(self, mock_db, mock_insert, mock_delete, mock_annotator):
        """Favouriting an object clears any hidden mark on it"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([{'classification': 'hidden'}])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        previous = annotate_util.mark_object(self.user, 123, 'favourite')

        # ASSERT
        self.assertEqual(previous, 'hidden')
        mock_insert.assert_called_once()
        self.assertEqual(mock_insert.call_args[0][:3], (123, 'tags_dave', 'favourite'))
        mock_delete.assert_called_once()
        self.assertEqual(mock_delete.call_args[0][:3], (123, 'tags_dave', 'hidden'))

    @mock.patch('annotate_util.make_tag_annotator.make_annotator')
    @mock.patch('annotate_util.delete_annotation')
    @mock.patch('annotate_util.insert_annotation_db')
    @mock.patch('annotate_util.db_connect.remote')
    def test_hidden_displaces_favourite(self, mock_db, mock_insert, mock_delete, mock_annotator):
        """Hiding an object clears any favourite mark on it"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([{'classification': 'favourite'}])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        previous = annotate_util.mark_object(self.user, 123, 'hidden')

        # ASSERT
        self.assertEqual(previous, 'favourite')
        self.assertEqual(mock_insert.call_args[0][:3], (123, 'tags_dave', 'hidden'))
        self.assertEqual(mock_delete.call_args[0][:3], (123, 'tags_dave', 'favourite'))

    @mock.patch('annotate_util.make_tag_annotator.make_annotator')
    @mock.patch('annotate_util.delete_annotation')
    @mock.patch('annotate_util.insert_annotation_db')
    @mock.patch('annotate_util.db_connect.remote')
    def test_repeating_a_mark_is_idempotent(self, mock_db, mock_insert, mock_delete, mock_annotator):
        """Re-marking an object it already holds writes the mark and deletes nothing"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([{'classification': 'favourite'}])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        previous = annotate_util.mark_object(self.user, 123, 'favourite')

        # ASSERT
        self.assertEqual(previous, 'favourite')
        mock_insert.assert_called_once()
        mock_delete.assert_not_called()

    @mock.patch('annotate_util.make_tag_annotator.make_annotator')
    @mock.patch('annotate_util.delete_annotation')
    @mock.patch('annotate_util.insert_annotation_db')
    @mock.patch('annotate_util.db_connect.remote')
    def test_none_clears_whichever_mark_is_held(self, mock_db, mock_insert, mock_delete, mock_annotator):
        """A mark of None deletes the mark held and inserts nothing"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([{'classification': 'hidden'}])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        previous = annotate_util.mark_object(self.user, 123, None)

        # ASSERT
        self.assertEqual(previous, 'hidden')
        mock_insert.assert_not_called()
        self.assertEqual(mock_delete.call_args[0][:3], (123, 'tags_dave', 'hidden'))

    @mock.patch('annotate_util.make_tag_annotator.make_annotator')
    @mock.patch('annotate_util.delete_annotation')
    @mock.patch('annotate_util.insert_annotation_db')
    @mock.patch('annotate_util.db_connect.remote')
    def test_clears_both_marks_when_an_object_holds_both(self, mock_db, mock_insert, mock_delete, mock_annotator):
        """An object left holding both marks by /api/annotate/ is tolerated"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([
            {'classification': 'favourite'}, {'classification': 'hidden'}])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        annotate_util.mark_object(self.user, 123, None)

        # ASSERT
        deleted = sorted(call[0][2] for call in mock_delete.call_args_list)
        self.assertEqual(deleted, ['favourite', 'hidden'])

    @mock.patch('annotate_util.make_tag_annotator.make_annotator')
    @mock.patch('annotate_util.db_connect.remote')
    def test_rejects_an_unknown_mark(self, mock_db, mock_annotator):
        """Only favourite, hidden and None are marks"""
        with self.assertRaises(annotate_util.AnnotationError):
            annotate_util.mark_object(self.user, 123, 'interesting')

    @mock.patch('annotate_util.make_tag_annotator.make_annotator')
    @mock.patch('annotate_util.insert_annotation_db')
    @mock.patch('annotate_util.db_connect.remote')
    def test_provisions_the_tag_annotator(self, mock_db, mock_insert, mock_annotator):
        """The user's tags_ annotator is created lazily on the write path"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        annotate_util.mark_object(self.user, 123, 'favourite')

        # ASSERT
        mock_annotator.assert_called_once_with(mock_db.return_value, 'dave', 3)


class MarksForObjectsTest(unittest.TestCase):
    """Tests for the marks_for_objects helper."""

    @mock.patch('annotate_util.db_connect.remote')
    def test_returns_a_mark_per_object(self, mock_db):
        """The marks held by one topic over the ids given come back as a dict"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([
            {'diaObjectId': 1, 'classification': 'favourite'},
            {'diaObjectId': 2, 'classification': 'hidden'}])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        marks = annotate_util.marks_for_objects('tags_dave', [1, 2, 3])

        # ASSERT
        self.assertEqual(marks, {1: 'favourite', 2: 'hidden'})

    @mock.patch('annotate_util.db_connect.remote')
    def test_parameterises_one_placeholder_per_id(self, mock_db):
        """Ids are bound as parameters, never interpolated"""
        # ARRANGE
        cursor = MagicMock()
        cursor.__iter__.return_value = iter([])
        mock_db.return_value.cursor.return_value = cursor

        # ACT
        annotate_util.marks_for_objects('tags_dave', [1, 2, 3])

        # ASSERT
        query, params = cursor.execute.call_args[0]
        self.assertIn('IN (%s, %s, %s)', query)
        self.assertEqual(params, ('tags_dave', 'favourite', 'hidden', 1, 2, 3))

    @mock.patch('annotate_util.db_connect.remote')
    def test_no_query_for_an_empty_id_list(self, mock_db):
        """An empty list of ids is an empty result, not a malformed IN clause"""
        # ACT
        marks = annotate_util.marks_for_objects('tags_dave', [])

        # ASSERT
        self.assertEqual(marks, {})
        mock_db.assert_not_called()


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
