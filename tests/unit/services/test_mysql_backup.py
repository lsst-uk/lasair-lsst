import context
#import mysql_backup
import unittest


class MySQLBackupDumpTest(unittest.TestCase):
    """Placeholder"""


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
    