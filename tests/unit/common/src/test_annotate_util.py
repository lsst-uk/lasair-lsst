import context
import annotate_util
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock


class AnnotateUtilTest(unittest.TestCase):
    """Tests for annotation utils."""

    @mock.patch('annotate_util.Producer')
    def test_insert_annotation_kafka(self, mock_producer):
        annotate_util.lasair_settings.ANNOTATION_TOPIC = 'asdf'
        annotate_util.insert_annotation_kafka(123, 'test_topic', 'test_class', 'v1', 'expl', '{}', 'test_url')
        mock_producer.return_value.produce.assert_called_once_with('asdf',
            '{"diaObjectId": 123, "topic": "test_topic", "classification": "test_class", "version": "v1", '
            '"explanation": "expl", "classdict": "{}", "url": "test_url"}')
        mock_producer.return_value.flush.assert_called_once()

    def test_insert_annotations_kafka(self):
        # not required as tested by above
        pass

    def test_insert_annotation_db(self):
        self.assertTrue(False)  # not implemented

    def test_delete_annotation(self):
        self.assertTrue(False)  # not implemented

    def test_classifications_for_object(self):
        self.assertTrue(False)  # not implemented

    def test_objects_for_classification(self):
        self.assertTrue(False)  # not implemented


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
