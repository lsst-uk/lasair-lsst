import context
import unittest
from unittest.mock import MagicMock
import make_tag_annotator

class TestMakeAnnotator(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value = self.mock_cursor

    def test_make_annotator_executes_parameterised_insert(self):
        """The username reaches the database as a parameter, not as SQL"""
        # ACT
        make_tag_annotator.make_annotator(self.mock_db, "alice", 123)

        # ASSERT
        expected_query = (
            'INSERT IGNORE INTO annotators (topic, active, public, user) '
            'VALUES (%s, 1, 0, %s)'
        )
        self.mock_cursor.execute.assert_called_once_with(
            expected_query, ('tags_alice', 123))

    def test_cursor_created_with_expected_arguments(self):
        make_tag_annotator.make_annotator(self.mock_db, "alice", 1)

        self.mock_db.cursor.assert_called_once_with(
            buffered=True,
            dictionary=True
        )

    def test_database_errors_are_raised(self):
        """A failed insert must not be reported as success"""
        # ARRANGE
        self.mock_cursor.execute.side_effect = Exception('database is down')

        # ACT / ASSERT
        with self.assertRaises(Exception):
            make_tag_annotator.make_annotator(self.mock_db, "alice", 1)


if __name__ == "__main__":
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
