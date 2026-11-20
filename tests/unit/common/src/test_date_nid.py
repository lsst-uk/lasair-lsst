import context
import date_nid
import datetime
import unittest
from unittest import mock


def fixed_now(year, month, day, hour):
    """Build a datetime subclass whose now() returns a fixed local time."""

    class FixedDatetime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(year, month, day, hour, 0, 0)

    return FixedDatetime


class DateNIDTest(unittest.TestCase):

    def test_days_ago_is_zero_for_nid_now(self):
        # ARRANGE: A FIXED CLOCK, SO THE TWO READS CANNOT STRADDLE THE 4-HOUR ROLLOVER
        with mock.patch('date_nid.datetime.datetime', fixed_now(2026, 11, 20, 12)):
            nid = date_nid.nid_now()

            # ACT
            daysAgo = date_nid.nid_to_days_ago(nid)

        # ASSERT
        self.assertEqual(daysAgo, 0)

    def test_days_ago_is_one_for_the_night_before_nid_now(self):
        # ARRANGE: A FIXED CLOCK, SO THE TWO READS CANNOT STRADDLE THE 4-HOUR ROLLOVER
        with mock.patch('date_nid.datetime.datetime', fixed_now(2026, 11, 20, 12)):
            nid = date_nid.nid_now() - 1

            # ACT
            daysAgo = date_nid.nid_to_days_ago(nid)

        # ASSERT
        self.assertEqual(daysAgo, 1)

    def test_days_ago_is_one_for_previous_night_after_evening_rollover(self):
        # ARRANGE: AT 22:00 LOCAL, nid_now() ALREADY POINTS AT TOMORROW
        evening = fixed_now(2026, 11, 20, 22)
        with mock.patch('date_nid.datetime.datetime', evening):
            tonight = date_nid.nid_now()
            self.assertEqual(date_nid.nid_to_date(tonight), '20261121')

            # ACT
            daysAgo = date_nid.nid_to_days_ago(tonight - 1)

        # ASSERT
        self.assertEqual(daysAgo, 1)

    def test_days_ago_is_zero_for_nid_now_after_evening_rollover(self):
        # ARRANGE
        evening = fixed_now(2026, 11, 20, 22)
        with mock.patch('date_nid.datetime.datetime', evening):
            # ACT
            daysAgo = date_nid.nid_to_days_ago(date_nid.nid_now())

        # ASSERT
        self.assertEqual(daysAgo, 0)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
