import unittest, unittest.mock
from unittest.mock import patch

import context
import ann_filters


class FilterTest(unittest.TestCase):
    """Tests for ann_filters module"""

    def test_query_for_object(self):
        query = ("SELECT objects.diaObjectId, objects.nDiaSources FROM objects"
                 "WHERE objects.nDiaSources > 1 Order\nBy objects.nDiaSources")
        objList = ["1", "2", "3"]
        expected = ( "SELECT objects.diaObjectId, objects.nDiaSources FROM objects"
                     "WHERE objects.nDiaSources > 1  AND objects.diaObjectId IN (1,2,3) "
                     " ORDER BY  objects.nDiaSources")
        result = ann_filters.query_for_object(query, objList)
        print(result)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    import xmlrunner 
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    unittest.main()
