import unittest
from datetime import datetime, timedelta
import numpy as np
import cftime

import cm4twc


class TestTimeDomainAPI(unittest.TestCase):

    def test_timedomain_init_variants_standard_on_leap_year(self):
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2020-02-28 09:00:00Z',
            calendar='standard'
        )

        td2 = cm4twc.TimeDomain.from_start_end_step(
            start=datetime(2020, 2, 28, 9, 0, 0),
            end=datetime(2020, 3, 2, 9, 0, 0),
            step=timedelta(days=1)
        )

        td3 = cm4twc.TimeDomain.from_datetime_sequence(
            datetimes=(datetime(2020, 2, 28, 9, 0, 0),
                       datetime(2020, 2, 29, 9, 0, 0),
                       datetime(2020, 3, 1, 9, 0, 0),
                       datetime(2020, 3, 2, 9, 0, 0))
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    def test_timedomain_init_variants_gregorian_cal_on_leap_year(self):
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2020-02-28 09:00:00Z',
            calendar='gregorian'
        )

        td2 = cm4twc.TimeDomain.from_start_end_step(
            start=cftime.DatetimeGregorian(2020, 2, 28, 9, 0, 0),
            end=cftime.DatetimeGregorian(2020, 3, 2, 9, 0, 0),
            step=timedelta(days=1)
        )

        td3 = cm4twc.TimeDomain.from_datetime_sequence(
            datetimes=(cftime.DatetimeGregorian(2020, 2, 28, 9, 0, 0),
                       cftime.DatetimeGregorian(2020, 2, 29, 9, 0, 0),
                       cftime.DatetimeGregorian(2020, 3, 1, 9, 0, 0),
                       cftime.DatetimeGregorian(2020, 3, 2, 9, 0, 0))
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    def test_timedomain_init_variants_julian_cal_on_leap_year(self):
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2020-02-28 09:00:00Z',
            calendar='julian'
        )

        td2 = cm4twc.TimeDomain.from_start_end_step(
            start=cftime.DatetimeJulian(2020, 2, 28, 9, 0, 0),
            end=cftime.DatetimeJulian(2020, 3, 2, 9, 0, 0),
            step=timedelta(days=1)
        )

        td3 = cm4twc.TimeDomain.from_datetime_sequence(
            datetimes=(cftime.DatetimeJulian(2020, 2, 28, 9, 0, 0),
                       cftime.DatetimeJulian(2020, 2, 29, 9, 0, 0),
                       cftime.DatetimeJulian(2020, 3, 1, 9, 0, 0),
                       cftime.DatetimeJulian(2020, 3, 2, 9, 0, 0))
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    def test_timedomain_init_variants_noleap_cal_on_leap_year(self):
        # test on a leap year (e.g. 2020)
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2020-02-28 09:00:00Z',
            calendar='noleap'
        )

        td2 = cm4twc.TimeDomain.from_start_end_step(
            start=cftime.DatetimeNoLeap(2020, 2, 28, 9, 0, 0),
            end=cftime.DatetimeNoLeap(2020, 3, 3, 9, 0, 0),
            step=timedelta(days=1)
        )

        td3 = cm4twc.TimeDomain.from_datetime_sequence(
            datetimes=(cftime.DatetimeNoLeap(2020, 2, 28, 9, 0, 0),
                       cftime.DatetimeNoLeap(2020, 3, 1, 9, 0, 0),
                       cftime.DatetimeNoLeap(2020, 3, 2, 9, 0, 0),
                       cftime.DatetimeNoLeap(2020, 3, 3, 9, 0, 0))
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    def test_timedomain_init_variants_all_leap_cal_on_leap_year(self):
        # test on a leap year (e.g. 2020)
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2020-02-28 09:00:00Z',
            calendar='all_leap'
        )

        td2 = cm4twc.TimeDomain.from_start_end_step(
            start=cftime.DatetimeAllLeap(2020, 2, 28, 9, 0, 0),
            end=cftime.DatetimeAllLeap(2020, 3, 2, 9, 0, 0),
            step=timedelta(days=1)
        )

        td3 = cm4twc.TimeDomain.from_datetime_sequence(
            datetimes=(cftime.DatetimeAllLeap(2020, 2, 28, 9, 0, 0),
                       cftime.DatetimeAllLeap(2020, 2, 29, 9, 0, 0),
                       cftime.DatetimeAllLeap(2020, 3, 1, 9, 0, 0),
                       cftime.DatetimeAllLeap(2020, 3, 2, 9, 0, 0))
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    def test_timedomain_init_variants_360_day_cal_on_leap_year(self):
        # test on a leap year (e.g. 2020)
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2020-02-28 09:00:00Z',
            calendar='360_day'
        )

        td2 = cm4twc.TimeDomain.from_start_end_step(
            start=cftime.Datetime360Day(2020, 2, 28, 9, 0, 0),
            end=cftime.Datetime360Day(2020, 3, 1, 9, 0, 0),
            step=timedelta(days=1)
        )

        td3 = cm4twc.TimeDomain.from_datetime_sequence(
            datetimes=(cftime.Datetime360Day(2020, 2, 28, 9, 0, 0),
                       cftime.Datetime360Day(2020, 2, 29, 9, 0, 0),
                       cftime.Datetime360Day(2020, 2, 30, 9, 0, 0),
                       cftime.Datetime360Day(2020, 3, 1, 9, 0, 0))
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    @unittest.expectedFailure
    def test_timedomain_init_irregular_timestep_in_timestamp_sequence(self):
        # should fail because last timestep is shorter
        cm4twc.TimeDomain(
            timestamps=np.array([0, 2, 4, 5]),
            units='days since 2020-02-28 09:00:00Z',
            calendar='standard'
        )

    @unittest.expectedFailure
    def test_timedomain_init_irregular_timestep_in_datetime_sequence(self):
        # should fail because first timestep is longer
        cm4twc.TimeDomain.from_datetime_sequence(
            datetimes=(datetime(2020, 1, 1, 9, 0, 0),
                       datetime(2020, 1, 3, 9, 0, 0),
                       datetime(2020, 1, 4, 9, 0, 0),
                       datetime(2020, 1, 5, 9, 0, 0))
        )


class TestTimeDomainComparison(unittest.TestCase):

    def test_timedomain_compare_with_different_reference_dates(self):
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([1, 2, 3, 4]),
            units='days since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        td2 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2019-01-02 09:00:00Z',
            calendar='standard'
        )

        self.assertEqual(td1, td2)

        td3 = cm4twc.TimeDomain(
            timestamps=np.array([1, 2, 3, 4]),
            units='days since 2019-01-02 09:00:00Z',
            calendar='standard'
        )

        self.assertNotEqual(td1, td3)

    def test_timedomain_compare_with_different_units_of_time(self):
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]) * 86400,
            units='seconds since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        td2 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]) * 24,
            units='hours since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        td3 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    def test_timedomain_compare_with_different_alias_calendars(self):
        for cal, alias in cm4twc.time_._supported_calendar_mapping.items():
            if not cal == alias:

                td1 = cm4twc.TimeDomain(
                    timestamps=np.array([0, 1, 2, 3]),
                    units='days since 2019-01-01 09:00:00Z',
                    calendar=cal
                )

                td2 = cm4twc.TimeDomain(
                    timestamps=np.array([0, 1, 2, 3]),
                    units='days since 2019-01-01 09:00:00Z',
                    calendar=alias
                )

                try:
                    self.assertEqual(td1, td2)
                except AssertionError as e:
                    raise AssertionError(
                        "The calendar '{}' and its alias '{}' are not "
                        "found equal.".format(cal, alias)) from e

    def test_timedomain_compare_with_different_dtypes(self):
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3], dtype=np.float32),
            units='days since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        td2 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3], dtype=np.float64),
            units='days since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        td3 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3], dtype=np.int),
            units='days since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        self.assertEqual(td1, td2)
        self.assertEqual(td1, td3)
        self.assertEqual(td2, td3)

    def test_timedomain_compare_with_different_lengths(self):
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3, 4]),
            units='days since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        td2 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2019-01-01 09:00:00Z',
            calendar='standard'
        )

        self.assertNotEqual(td1, td2)

    @unittest.expectedFailure
    def test_timedomain_compare_with_different_non_alias_calendars(self):
        # should fail because it cannot compare across different calendars
        td1 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2019-01-01 09:00:00Z',
            calendar='gregorian'
        )

        td2 = cm4twc.TimeDomain(
            timestamps=np.array([0, 1, 2, 3]),
            units='days since 2019-01-01 09:00:00Z',
            calendar='julian'
        )

        self.assertEqual(td1, td2)


class TestClock(unittest.TestCase):

    def setUp(self):
        self.td_a = cm4twc.TimeDomain(
            timestamps=(np.array([0, 1, 2, 3, 4, 5, 6]) * 86400.),
            units='seconds since 1970-01-02 00:00:00',
            calendar='standard'
        )

        self.td_b = cm4twc.TimeDomain(
            timestamps=(np.array([1, 3, 5, 7]) * 86400),
            units='seconds since 1970-01-01 00:00:00',
            calendar='gregorian'
        )

        self.td_c = cm4twc.TimeDomain(
            timestamps=np.array([1, 4, 7]),
            units='days since 1970-01-01 00:00:00',
            calendar='gregorian'
        )

        self.td_d = cm4twc.TimeDomain(
            timestamps=np.array([1, 4, 7, 10]),
            units='days since 1970-01-01 00:00:00',
            calendar='gregorian'
        )

        self.exp_a = [True, True, True, True, True, True, True]

        self.exp_b = [True, False, True, False, True, False, True]

        self.exp_c = [True, False, False, True, False, False, True]

    def test_clock_init(self):
        clock = cm4twc.time_.Clock(surfacelayer_timedomain=self.td_a,
                                   subsurface_timedomain=self.td_b,
                                   openwater_timedomain=self.td_c)

        self.assertEqual(clock._surfacelayer_switch.tolist(), self.exp_a)
        self.assertEqual(clock._subsurface_switch.tolist(), self.exp_b)
        self.assertEqual(clock._openwater_switch.tolist(), self.exp_c)

    @unittest.expectedFailure
    def test_clock_init_timedomain_mismatch(self):
        # should fail because end date do not match
        cm4twc.time_.Clock(surfacelayer_timedomain=self.td_a,
                           subsurface_timedomain=self.td_b,
                           openwater_timedomain=self.td_d)

    def test_clock_iteration(self):
        clock = cm4twc.time_.Clock(surfacelayer_timedomain=self.td_a,
                                   subsurface_timedomain=self.td_b,
                                   openwater_timedomain=self.td_c)

        out_a, out_b, out_c = list(), list(), list()

        for a, b, c in clock:
            out_a.append(a)
            out_b.append(b)
            out_c.append(c)

        self.assertEqual(out_a, self.exp_a[:-1])
        self.assertEqual(out_b, self.exp_b[:-1])
        self.assertEqual(out_c, self.exp_c[:-1])


if __name__ == '__main__':
    unittest.main()
