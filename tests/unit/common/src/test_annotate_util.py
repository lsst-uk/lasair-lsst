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
        mock_producer.return_value.produce.assert_called_once_with('asdf',
            '{"diaObjectId": 123, "topic": "test_topic", "classification": "test_class", "version": "v1", '
            '"explanation": "expl", "classdict": "{}", "url": "test_url"}')
        mock_producer.return_value.flush.assert_called_once()

    def test_insert_annotations_kafka(self):
        """Test insert_annotations_kafka function"""
        # not required as tested by above
        pass

    def test_insert_annotation_db(self):
        """Test insert_annotation_db function"""
        self.assertTrue(False)  # not implemented

    def test_delete_annotation(self):
        """Test delete_annotation function"""
        self.assertTrue(False)  # not implemented

    @mock.patch('annotate_util.db_connect.remote')
    def test_delete_annotation_tags(self, mock_db):
        """Test delete_annotation function for tags"""
        annotate_util.delete_annotation(123, 'tags_test_topic', 'test_class')
        mock_db.return_value.cursor.return_value.execute.assert_called_with(
            'DELETE FROM annotations WHERE diaObjectId=123 AND topic="tags_test_topic" AND classification=test_class')

    @mock.patch('annotate_util.db_connect.remote')
    def test_delete_annotation_error(self, mock_db):
        """Test that delete_annotation function raises exception if called without classification on a tags topic"""
        with self.assertRaises(annotate_util.AnnotationError):
            annotate_util.delete_annotation(123, 'tags_test_topic')

    def test_classifications_for_object(self):
        """Test classifications_for_object function"""
        self.assertTrue(False)  # not implemented

    def test_objects_for_classification(self):
        """Test objects_for_classification function"""
        self.assertTrue(False)  # not implemented


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
