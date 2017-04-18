# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import amazonndt
import unittest
import datetime as dt


class TestAmazonDate(unittest.TestCase):

    def date_validation_helper(self, amazon_date_str, expected_start, expected_duration):
        obj = amazonndt.AmazonDate(amazon_date_str)
        self.assertEqual(obj.start, expected_start)
        self.assertEqual(obj.duration, expected_duration)
        self.assertEqual(obj.amazon_date_str, amazon_date_str)
        return obj # For further interrogation


    def test_handle_day(self):
        self.date_validation_helper(
            amazon_date_str="2017-02-05",
            expected_start=dt.datetime(year=2017, month=2, day=5),
            expected_duration=dt.timedelta(hours=24))

    def test_handle_week(self):
        self.date_validation_helper(
            amazon_date_str="2015-W49",
            expected_start=dt.datetime(year=2015, month=12, day=7),
            expected_duration=dt.timedelta(days=7))

    def test_handle_weekend(self):
        self.date_validation_helper(
            amazon_date_str="2015-W49-WE",
            expected_start=dt.datetime(year=2015, month=12, day=12),
            expected_duration=dt.timedelta(days=2))

    def test_handle_month(self):
        self.date_validation_helper(
            amazon_date_str="2015-12",
            expected_start=dt.datetime(year=2015, month=12, day=1),
            expected_duration=dt.timedelta(days=31))

    def test_handle_year(self):
        self.date_validation_helper(
            amazon_date_str="2015",
            expected_start=dt.datetime(year=2015, month=1, day=1),
            expected_duration=dt.timedelta(days=365))

    def test_handle_decade(self):
        self.date_validation_helper(
            amazon_date_str="201X",
            expected_start=dt.datetime(year=2010, month=1, day=1),
            expected_duration=dt.timedelta(days=(365*8 + 366*2)))


    # All the seasons are currently meteorological time
    # There is also astronomical time
    # But this is GEFN
    def test_handle_winter(self):
        self.date_validation_helper(
            amazon_date_str="2014-WI",
            expected_start=dt.datetime(year=2014, month=12, day=1),
            expected_duration=dt.timedelta(days=90)) # til Feb 28

    def test_handle_winter_leap(self):
        self.date_validation_helper(
            amazon_date_str="2015-WI",
            expected_start=dt.datetime(year=2015, month=12, day=1),
            expected_duration=dt.timedelta(days=91)) # til Feb 29

    def test_handle_fall(self):
        self.date_validation_helper(
            amazon_date_str="2015-FA",
            expected_start=dt.datetime(year=2015, month=9, day=1),
            expected_duration=dt.timedelta(days=91)) # till Nov 30

    def test_handle_summer(self):
        self.date_validation_helper(
            amazon_date_str="2015-SU",
            expected_start=dt.datetime(year=2015, month=6, day=1),
            expected_duration=dt.timedelta(days=92)) # til Aug 31

    def test_handle_spring(self):
        self.date_validation_helper(
            amazon_date_str="2015-SP",
            expected_start=dt.datetime(year=2015, month=3, day=1),
            expected_duration=dt.timedelta(days=92)) # til May 31


    def test_handle_now(self):
        # Needs special handling b/c "now" is variable
        now = dt.datetime.now()
        self.date_validation_helper(
            amazon_date_str="PRESENT_REF",
            expected_start=dt.datetime(year=now.year, month=now.month, day=now.day),
            expected_duration=dt.timedelta(hours=24))


class TestAmazonDuration(unittest.TestCase):

    def test_raises_on_parse_error(self):
        with self.assertRaises(ValueError):
            obj = amazonndt.AmazonDuration("blah")

    def test_minutes(self):
        obj = amazonndt.AmazonDuration("PT10M")
        self.assertEqual(dt.timedelta(minutes=10), obj.timedelta)

    def test_hours(self):
        obj = amazonndt.AmazonDuration("PT5H")
        self.assertEqual(dt.timedelta(hours=5), obj.timedelta)

    def test_days(self):
        obj = amazonndt.AmazonDuration("P3D")
        self.assertEqual(dt.timedelta(days=3), obj.timedelta)

    def test_seconds(self):
        obj = amazonndt.AmazonDuration("PT45S")
        self.assertEqual(dt.timedelta(seconds=45), obj.timedelta)

    def test_weeks(self):
        obj = amazonndt.AmazonDuration("P8W")
        self.assertEqual(dt.timedelta(weeks=8), obj.timedelta)

    @unittest.skip("TODO: Need to tighten up the definition for handling Months/Years")
    def test_years(self):
        obj = amazonndt.AmazonDuration("P7Y")
        self.assertEqual(dt.timedelta(weeks=52*7), obj.timedelta)

    @unittest.skip("TODO: Need to tighten up the definition for handling Months/Years")
    def test_months(self):
        obj = amazonndt.AmazonDuration("P4M")
        self.assertEqual(dt.timedelta(weeks=16), obj.timedelta)

    def test_hours_and_minutes(self):
        obj = amazonndt.AmazonDuration("PT5H10M")
        self.assertEqual(dt.timedelta(hours=5, minutes=10), obj.timedelta)

    @unittest.skip("TODO: Need to tighten up the definition for handling Months/Years")
    def test_years_hours_and_minutes(self):
        obj = amazonndt.AmazonDuration("P2YT3H10M")
        self.assertEqual(dt.timedelta(weeks=2*52, hours=3, minutes=10), obj.timedelta)

    def test_all_values(self):
        obj = amazonndt.AmazonDuration("P3Y4M2W1DT5H10M42S")
        # Just let it run and make sure it doesn't blow up for now
        # TODO: Also needs tighter definition for handling Months/Years


class TestAmazonFourDigitNumber(unittest.TestCase):
    def test_instantiation(self):
        obj = amazonndt.AmazonFourDigitNumber("1234")
        self.assertEqual(obj.fdn, 1234)
        self.assertEqual(obj.fdn_str, "1234")

    def test_negative_out_of_bounds(self):
        with self.assertRaises(ValueError):
            obj = amazonndt.AmazonFourDigitNumber("-1")

    def test_positive_out_of_bounds(self):
        with self.assertRaises(ValueError):
            obj = amazonndt.AmazonFourDigitNumber("10000")

    def test_not_a_number(self):
        with self.assertRaises(ValueError):
            obj = amazonndt.AmazonFourDigitNumber("abcd")

    def test_none(self):
        with self.assertRaises(ValueError):
            obj = amazonndt.AmazonFourDigitNumber(None)


class TestAmazonNumber(unittest.TestCase):
    def test_instantiation(self):
        obj = amazonndt.AmazonNumber("1234")
        self.assertEqual(obj.number, 1234)
        self.assertEqual(obj.number_str, "1234")

    def test_negative_number(self):
        # assuming Amazon handles negative numbers, need to test out
        obj = amazonndt.AmazonNumber("-1234")
        self.assertEqual(obj.number, -1234)
        self.assertEqual(obj.number_str, "-1234")

    def test_not_a_number(self):
        with self.assertRaises(ValueError):
            obj = amazonndt.AmazonNumber("abcd")

    def test_none(self):
        with self.assertRaises(ValueError):
            obj = amazonndt.AmazonNumber(None)



class TestAmazonTime(unittest.TestCase):
    def test_instantiation(self):
        obj = amazonndt.AmazonTime("blah")
        self.assertTrue(obj is not None)


if __name__ == "__main__":
    unittest.main()