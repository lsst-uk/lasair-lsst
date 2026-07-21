import context
import annotate_util
import unittest
from unittest.mock import MagicMock


class AnnotateUtilTest(unittest.TestCase):
    """Tests for annotation utils."""

    def test_insert_annotations_kafka(self):
        self.assertTrue(False)  # not implemented

    def test_insert_annotation_kafka(self):
        self.assertTrue(False)  # not implemented

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
