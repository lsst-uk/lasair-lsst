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
        mock_msl = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_msl
        mock_msl.cursor.return_value = mock_cursor

        expected_delete = (
            'DELETE FROM annotations '
            'WHERE diaObjectId=123 AND topic="test_topic"'
        )
        expected_insert = (
            "INSERT INTO annotations ("
            "diaObjectId, topic, version, classification, explanation, classdict, url"
            ") VALUES ("
            "'123', 'test_topic', 'v1', 'test_class', 'expl', '{}', 'test_url')"
        )
        annotate_util.insert_annotation_db(123, 'test_topic', 'test_class', 'v1', 'expl', '{}', 'test_url')
        mock_cursor.execute.assert_any_call(expected_delete)
        mock_cursor.execute.assert_any_call(expected_insert)

    @mock.patch('db_connect.remote')
    def test_delete_annotation(self, mock_db):
        """Test delete_annotation function"""
        """Test delete_annotation function for tags"""
        annotate_util.delete_annotation(123, 'test_topic', 'test_class')
        expected_delete = (
            'DELETE FROM annotations WHERE diaObjectId=123 AND topic="test_topic"'
            )
        mock_db.return_value.cursor.return_value.execute.assert_called_with(expected_delete)

    @mock.patch('annotate_util.db_connect.remote')
    def test_delete_annotation_tags(self, mock_db):
        """Test delete_annotation function for tags"""
        annotate_util.delete_annotation(123, 'tags_test_topic', 'test_class')
        expected_delete = (
            'DELETE FROM annotations WHERE diaObjectId=123 AND topic="tags_test_topic" '
            'AND classification="test_class"'
            )
        mock_db.return_value.cursor.return_value.execute.assert_called_with(expected_delete)

    @mock.patch('annotate_util.db_connect.remote')
    def test_delete_annotation_error(self, mock_db):
        """Test that delete_annotation function raises exception if called without classification on a tags topic"""
        with self.assertRaises(annotate_util.AnnotationError):
            annotate_util.delete_annotation(123, 'tags_test_topic')

    @mock.patch('annotate_util.db_connect.remote')
    def test_classifications_for_object(self, mock_db):
        """Test classifications_for_object function"""
        expected_select = (
            'SELECT classification FROM annotations '
            'WHERE topic="test_topic" AND diaObjectId=123'
            )
        annotate_util.classifications_for_object('test_topic', 123)
        mock_db.return_value.cursor.return_value.execute.assert_called_with(expected_select)

    @mock.patch('annotate_util.db_connect.remote')
    def test_objects_for_classification(self, mock_db):
        """Test objects_for_classification function"""
        expected_select = (
            'SELECT diaObjectId FROM annotations '
            'WHERE topic="test_topic" AND classification="apple"'
            )
        annotate_util.objects_for_classification('test_topic', 'apple')
        mock_db.return_value.cursor.return_value.execute.assert_called_with(expected_select)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
