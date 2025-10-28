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

        # A small cone and a large cone
        wl_id = 1
        cones = [
            {'cone_id':1, 'myRA':1.0, 'myDecl':1.0, 'radius':1.0,   'name':'small'},
            {'cone_id':2, 'myRA':2.0, 'myDecl':1.0, 'radius':100.0, 'name':'large'},
        ]

        # A set of objects to run against
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = [
            { "diaObjectId": 123, "ra": 1.0001, "decl": 1.0001 }, # in small
            { "diaObjectId": 124, "ra": 1.0001, "decl": 1.0005 }, # neither
            { "diaObjectId": 125, "ra": 2.0000, "decl": 1.0200 }, # in large
            { "diaObjectId": 126, "ra": 2.0500, "decl": 1.0000 }, # neither
        ]

        # expected results
        expect_results = [
            '(1,1,"123",0.51,"small")',
            '(1,2,"125",72.00,"large")',
        ]

        mock_session = MagicMock()
        mock_session.cursor.return_value = mock_cursor
        for (cone,expect_result) in zip(cones, expect_results):
            result = run_crossmatch.crossmatch(mock_session, wl_id, 
                cone['cone_id'], cone['myRA'], cone['myDecl'], cone['name'], cone['radius'])
            # check that we got the expected number of hits
            self.assertEqual(result, 1)
            # check that execute got called with the expected values
            self.assertRegex(mock_cursor.execute.call_args.args[0].replace(" ", ""), expect_result)

if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
