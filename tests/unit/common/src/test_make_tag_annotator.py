import context
import unittest
from unittest.mock import MagicMock
import make_tag_annotator

class TestMakeAnnotator(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value = self.mock_cursor

    def test_make_annotator_executes_insert(self):
        make_tag_annotator.make_annotator(
            self.mock_db, "alice", 123)

        expected_query = (
            'INSERT INTO annotators (topic, active, public, user) '
            'VALUES ("tags_alice", 1, 0, 123)'
        )
        self.mock_cursor.execute.assert_called_once_with(expected_query)

    def test_cursor_created_with_expected_arguments(self):
        make_tag_annotator.make_annotator(
            self.mock_db, "alice", 1)

        self.mock_db.cursor.assert_called_once_with(
            buffered=True,
            dictionary=True
        )

if __name__ == "__main__":
    unittest.main()
