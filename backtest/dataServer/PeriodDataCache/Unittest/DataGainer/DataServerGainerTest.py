import unittest
from dataServer.PeriodDataCache.DataGainer.DataServerGainer import DataServerGainer
import datetime


class DataServerGainerTest(unittest.TestCase):
    def setUp(self):
        self.gainer = DataServerGainer()

    def test(self):
        instrument = 'a1609'
        period = '60'
        start = datetime.datetime(2016, 5, 1)
        end = datetime.datetime(2016, 5, 31)
        print self.gainer.get_data(instrument, period, start, end)