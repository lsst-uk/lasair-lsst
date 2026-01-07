import context
from run_crossmatch_optimised import run_crossmatch 
import unittest
from unittest.mock import MagicMock


class RunCrossMatchOptimisedTest(unittest.TestCase):
    """Unit tests for the run_crossmatch function."""

    def test_crossmatch(self):
        """Test the crossmatch function. We return 2 rows, of which one should match."""

        # A small cone and a large cone
        wl_id = 1
        cones = [
            {'cone_id': 101, 'ra': 1.0, 'decl': 1.0, 'radius': 1.0, 'name': 'small'},
            {'cone_id': 102, 'ra': 2.0, 'decl': 1.0, 'radius': 100.0, 'name': 'large'},
        ]

        # A set of objects to run against
        mock_cursor = MagicMock()

        dbRows = [
            {"diaObjectId": 123, "ra": 1.0001, "decl": 1.0001},  # in small
            {"diaObjectId": 124, "ra": 1.0001, "decl": 1.0005},  # neither
            {"diaObjectId": 125, "ra": 2.0000, "decl": 1.0200},  # in large
            {"diaObjectId": 126, "ra": 2.0500, "decl": 1.0000},  # neither
        ]

        mock_cursor.fetchall.side_effect = [cones, dbRows, dbRows, [{"count(*)": 1}], dbRows]

        # expected results
        expect_results = [
            '(1,101,"123",0.51,"small")',
            '(1,102,"125",72.00,"large")',
        ]

        mock_session = MagicMock()
        mock_session.cursor.return_value = mock_cursor
        type(mock_session).__name__ = "Connection"
        result, message = run_crossmatch(mock_session, radius=5.0, wl_id=wl_id, unittest=True)
        # check that we got the expected number of hits
        self.assertEqual(result, 2)

    def test_empty_db_rows(self):
        """Test the crossmatch function with empty database rows."""

        wl_id = 2
        cones = [
            {'cone_id': 201, 'ra': 3.0, 'decl': 3.0, 'radius': 1.0, 'name': 'test_cone'},
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [cones, []]  # No database rows

        mock_session = MagicMock()
        mock_session.cursor.return_value = mock_cursor
        type(mock_session).__name__ = "Connection"

        result, message = run_crossmatch(mock_session, radius=5.0, wl_id=wl_id, unittest=True)
        self.assertEqual(result, 0)
        self.assertIn("0 LSST objects have been associated", message)

    def test_no_cones(self):
        """Test the crossmatch function with no cones."""

        wl_id = 3
        cones = []  # No cones

        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [cones, []]

        mock_session = MagicMock()
        mock_session.cursor.return_value = mock_cursor
        type(mock_session).__name__ = "Connection"

        result, message = run_crossmatch(mock_session, radius=5.0, wl_id=wl_id, unittest=True)
        self.assertEqual(result, 0)
        self.assertIn("0 LSST objects have been associated", message)

    def test_large_radius(self):
        """Test the crossmatch function with a large radius."""

        wl_id = 4
        cones = [
            {'cone_id': 301, 'ra': 4.0, 'decl': 4.0, 'radius': 2000.0, 'name': 'large_radius'},
        ]

        mock_cursor = MagicMock()
        dbRows = [
            {"diaObjectId": 401, "ra": 4.0001, "decl": 4.0001},  # within large radius
        ]
        mock_cursor.fetchall.side_effect = [cones, dbRows, [{"count(*)": 1}], dbRows]

        mock_session = MagicMock()
        mock_session.cursor.return_value = mock_cursor
        type(mock_session).__name__ = "Connection"

        result, message = run_crossmatch(mock_session, radius=5.0, wl_id=wl_id, unittest=True)
        self.assertEqual(result, 1)
        self.assertIn("1 LSST objects have been associated", message)

    def test_no_matches(self):
        """Test the crossmatch function with no matches."""

        wl_id = 5
        cones = [
            {'cone_id': 401, 'ra': 5.0, 'decl': 5.0, 'radius': 1.0, 'name': 'isolated'},
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [cones, []]  # No matches

        mock_session = MagicMock()
        mock_session.cursor.return_value = mock_cursor
        type(mock_session).__name__ = "Connection"

        result, message = run_crossmatch(mock_session, radius=5.0, wl_id=wl_id, unittest=True)
        self.assertEqual(result, 0)
        self.assertIn("0 LSST objects have been associated", message)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
