import unittest
from dataServer.PeriodDataCache import PeriodDataCache
from dataServer.PeriodDataCache.Cacher.BaseCache import Cacher
from dataServer.PeriodDataCache.DataGainer.BaseDataGainer import DataGainer
import datetime


class _MockCacher(Cacher):
    def __init__(self):
        self.cache_table = {}

    @staticmethod
    def get_key(instrument, period, start, end):
        return '.'.join([instrument, period, str(start.date()), str(end.date())])

    def cache_data(self, instrument, period, start, end, data):
        self.cache_table[self.get_key(instrument, period, start, end)] = data

    def get_data(self, instrument, period, start, end):
        return self.cache_table.get(self.get_key(instrument, period, start, end))


class _MockDataGainer(DataGainer):
    def __init__(self):
        self.gain_count = 0

    def get_data(self, instrument, period, start, end):
        self.gain_count += 1
        return ['%s.%s.%s.%s' % (instrument, period, str(start.date()), str(end.date()))]


class PeriodDataCacheTest(unittest.TestCase):
    def setUp(self):
        self.gainer = _MockDataGainer()
        self.cacher = _MockCacher()
        self.pdc = PeriodDataCache(self.cacher, self.gainer)

    def test(self):
        # get_no_cache_data
        start = datetime.datetime(2016, 1, 1)
        end = datetime.datetime(2016, 8, 31)
        instrument = 'a1609'
        period = '01'
        rt = self.pdc.get_data(instrument, period, start, end)
        self.assertEqual(self.gainer.gain_count, 8)
        self.assertListEqual(
            ['a1609.01.2016-01-01.2016-01-31', 'a1609.01.2016-02-01.2016-02-29', 'a1609.01.2016-03-01.2016-03-31',
             'a1609.01.2016-04-01.2016-04-30', 'a1609.01.2016-05-01.2016-05-31', 'a1609.01.2016-06-01.2016-06-30',
             'a1609.01.2016-07-01.2016-07-31', 'a1609.01.2016-08-01.2016-08-31'], rt)
        # get_all_cache_data
        self.gainer.gain_count = 0
        rt = self.pdc.get_data(instrument, period, start, end)
        self.assertEqual(self.gainer.gain_count, 0)
        self.assertListEqual(
            ['a1609.01.2016-01-01.2016-01-31', 'a1609.01.2016-02-01.2016-02-29', 'a1609.01.2016-03-01.2016-03-31',
             'a1609.01.2016-04-01.2016-04-30', 'a1609.01.2016-05-01.2016-05-31', 'a1609.01.2016-06-01.2016-06-30',
             'a1609.01.2016-07-01.2016-07-31', 'a1609.01.2016-08-01.2016-08-31'], rt)
        # get_part_cache_data
        self.gainer.gain_count = 0
        start = datetime.datetime(2015, 12, 01)
        end = datetime.datetime(2016, 9, 30)
        rt = self.pdc.get_data(instrument, period, start, end)
        self.assertEqual(self.gainer.gain_count, 2)
        self.assertListEqual(
            ['a1609.01.2015-12-01.2015-12-31', 'a1609.01.2016-01-01.2016-01-31', 'a1609.01.2016-02-01.2016-02-29',
             'a1609.01.2016-03-01.2016-03-31', 'a1609.01.2016-04-01.2016-04-30', 'a1609.01.2016-05-01.2016-05-31',
             'a1609.01.2016-06-01.2016-06-30', 'a1609.01.2016-07-01.2016-07-31', 'a1609.01.2016-08-01.2016-08-31',
             'a1609.01.2016-09-01.2016-09-30']
            , rt)
