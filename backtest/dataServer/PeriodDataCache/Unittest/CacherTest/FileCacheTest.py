import unittest
from dataServer.PeriodDataCache.Cacher.FileCache import FileCache
import datetime
import os


class FileCacheTest(unittest.TestCase):
    def setUp(self):
        self.data_path = '/Users/renren1/test'
        self.file_cache = FileCache(self.data_path)
        self.instrument = 'a1609'
        self.period = '01'
        self.start = datetime.datetime(2016, 01, 01)
        self.end = datetime.datetime(2016, 01, 31)

    def tearDown(self):
        try:
            os.remove(self.file_cache.get_file_path(self.instrument, self.period, self.start, self.end))
        except:
            pass

    def test_no_cache(self):
        # no cache
        self.assertIsNone(self.file_cache.get_data(self.instrument, self.period, self.start, self.end))

    def test_cache_data(self):
        # cache data
        data = [(self.instrument, self.period, self.start, self.end)]
        self.file_cache.cache_data(self.instrument, self.period, self.start, self.end, data)
        self.assertListEqual(data,
                             FileCache(self.data_path).get_data(self.instrument, self.period, self.start, self.end))
