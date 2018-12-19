import unittest
import datetime
from Common.utility import TradingTime

__all__ = ['TradingTimeTest']


class TradingTimeTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_trading(self):
        TradingTime.is_trading()
        self.assertEqual(TradingTime.is_trading(datetime.datetime(2016, 8, 22, 11, 29, 00)), True)
        self.assertEqual(TradingTime.is_trading(datetime.datetime(2016, 8, 22, 11, 31, 00)), False)

    def test_is_close(self):
        self.assertTrue(TradingTime.is_close(datetime.datetime(2016, 8, 22, 15, 1, 00)))
        self.assertFalse(TradingTime.is_close(datetime.datetime(2016, 8, 22, 11, 31, 00)))
        TradingTime.is_close()

    def test_next_trading_time_delay(self):
        TradingTime.next_trading_time_delay()
        self.assertEqual(TradingTime.next_trading_time_delay(datetime.datetime(2016, 8, 22, 11, 31, 00)), 7140)
        self.assertEqual(TradingTime.next_trading_time_delay(datetime.datetime(2016, 8, 22, 13, 29, 00)), 60)

    def test_datetime_time_subtract(self):
        self.assertEqual(TradingTime.datetime_time_subtract(datetime.time(0, 0, 10), datetime.time(0, 0, 1)), 9)
        self.assertEqual(TradingTime.datetime_time_subtract(datetime.time(0, 1, 10), datetime.time(0, 0, 1)), 69)
        self.assertEqual(TradingTime.datetime_time_subtract(datetime.time(1, 1, 10), datetime.time(0, 0, 1)), 3669)

    def test_is_trading_day(self):
        print TradingTime.is_trading_day()
