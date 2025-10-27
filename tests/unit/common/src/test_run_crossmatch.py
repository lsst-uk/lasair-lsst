import context
import run_crossmatch
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock
from math import sqrt


class RunCrossmatchTest(unittest.TestCase):

    def test_distance(self):
        """Test the distance function."""
        # Not sure that this is really the best test case
        result = run_crossmatch.distance(0.0, 0.0, 1.0, 1.0)
        self.assertEqual(result, sqrt(2))

    @mock.patch('run_crossmatch.htmCircle')
    def test_crossmatch(self, mock_htmCircle):
        """Test the crossmatch function. We return 2 rows, of which one should match."""
        mock_htmCircle.htmCircleRegion.return_value = ''
        wl_id = 1
        cone_id = 1
        myRA = 1.2
        myDecl = 1.2
        name = "test"
        radius = 1.0
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = [
            {
                "diaObjectId": 123,
                "ra": 1.2001,
                "decl": 1.1999
            },
            {
                "diaObjectId": 456,
                "ra": 1.2005,
                "decl": 1.2
            }

        ]
        mock_session = MagicMock()
        mock_session.cursor.return_value = mock_cursor
        result = run_crossmatch.crossmatch(mock_session, wl_id, cone_id, myRA, myDecl, name, radius)
        # check that we got the expected number of hits
        self.assertEqual(result, 1)
        # check that execute got called with the expected values
        self.assertRegex(mock_cursor.execute.call_args.args[0].replace(" ", ""),
                         '1,1,"123",0.51,"test"')


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
