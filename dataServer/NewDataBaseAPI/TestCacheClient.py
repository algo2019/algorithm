import copy
import datetime

import CacheClient
import unittest
import Conf
import os
import datetime
from Common.CommonLogServer import mlogging
mlogging.Conf.DEBUG = True


class TestUpdateTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = CacheClient.UpdateTable()
        cls.table.create()

    @classmethod
    def tearDownClass(cls):
        Conf.get_gta_db(CacheClient.DB_TYPE.SQLITE, True)
        os.remove(Conf.CACHE_DB_PATH)

    def setUp(self):
        self.table.clear()

    def insert(self):
        self.code = 'al1701'
        self.period = '1m'
        self.lists = [['2016-01-01 10:45:00', '2016-02-01 10:45:00'], ['2016-03-01 10:45:00', '2016-03-05 10:45:00']]
        self.table._insert(self.code, self.period, self.lists)

    def test_insert(self):
        self.insert()
        self.assertListEqual(self.lists,
                             self.table.interval_sets_to_list(self.table.get_db_interval_sets(self.code, self.period)))

    def test_delete(self):
        self.insert()
        self.table._delete(self.code, self.period)
        self.assertListEqual(self.table.interval_sets_to_list(self.table.get_db_interval_sets(self.code, self.period)),
                             [])

    def test_update(self):
        self.insert()
        lists = [['2016-02-01 10:45:00', '2016-03-01 10:45:00']]
        self.table.update_interval(self.code, self.period, lists)
        self.assertListEqual(self.table.interval_sets_to_list(self.table.get_db_interval_sets(self.code, self.period)),
                             [['2016-01-01 10:45:00', '2016-03-05 10:45:00']])

        lists = [['2010-01-01 01:01:01', '2011-01-23 23:44:22'], ['2017-01-01 01:01:01', '2017-01-23 23:44:22']]
        self.table.update_interval(self.code, self.period, lists)
        self.assertListEqual(self.table.interval_sets_to_list(self.table.get_db_interval_sets(self.code, self.period)),
                             [['2010-01-01 01:01:01', '2011-01-23 23:44:22'],
                              ['2016-01-01 10:45:00', '2016-03-05 10:45:00'],
                              ['2017-01-01 01:01:01', '2017-01-23 23:44:22']]
                             )


class TestDailyTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = [
            [datetime.datetime(2016, 12, 30, 0, 0), 'SR705', 6810.0, 6848.0, 6791.0, 6826.0, 411420.0, 2808528.33,
             7057.0, 6513.0],
            [datetime.datetime(2017, 1, 3, 0, 0), 'SR705', 6848.0, 6848.0, 6727.0, 6739.0, 260194.0, 1760875.58, 7100.0,
             6552.0],
            [datetime.datetime(2017, 1, 4, 0, 0), 'SR705', 6748.0, 6842.0, 6742.0, 6808.0, 437568.0, 2976248.04, 7039.0,
             6497.0],
            [datetime.datetime(2017, 1, 5, 0, 0), 'SR705', 6812.0, 6880.0, 6804.0, 6847.0, 467312.0, 3197663.71, 7075.0,
             6529.0],
            [datetime.datetime(2017, 1, 6, 0, 0), 'SR705', 6850.0, 6854.0, 6773.0, 6791.0, 384392.0, 2617952.37, 7117.0,
             6569.0],
            [datetime.datetime(2017, 1, 9, 0, 0), 'SR705', 6780.0, 6868.0, 6773.0, 6836.0, 341562.0, 2330367.86, 7084.0,
             6538.0],
            [datetime.datetime(2017, 1, 10, 0, 0), 'SR705', 6826.0, 6832.0, 6787.0, 6811.0, 339302.0, 2309782.84,
             7096.0, 6550.0],
            [datetime.datetime(2017, 1, 11, 0, 0), 'SR705', 6800.0, 6920.0, 6784.0, 6870.0, 590898.0, 4059630.99,
             7080.0, 6534.0],
            [datetime.datetime(2017, 1, 12, 0, 0), 'SR705', 6895.0, 6912.0, 6849.0, 6856.0, 355994.0, 2448099.5, 7145.0,
             6595.0],
            [datetime.datetime(2017, 1, 13, 0, 0), 'SR705', 6868.0, 6890.0, 6792.0, 6818.0, 448928.0, 3071275.4, 7153.0,
             6601.0],
            [datetime.datetime(2017, 1, 16, 0, 0), 'SR705', 6822.0, 6892.0, 6815.0, 6837.0, 366362.0, 2509362.3, 7115.0,
             6567.0],
            [datetime.datetime(2017, 1, 17, 0, 0), 'SR705', 6839.0, 6855.0, 6780.0, 6827.0, 366164.0, 2497905.98,
             7123.0, 6575.0],
            [datetime.datetime(2017, 1, 18, 0, 0), 'SR705', 6835.0, 6903.0, 6822.0, 6869.0, 366870.0, 2515717.67,
             7095.0, 6549.0],
            [datetime.datetime(2017, 1, 19, 0, 0), 'SR705', 6871.0, 7004.0, 6850.0, 6991.0, 713254.0, 4950768.85,
             7132.0, 6582.0],
            [datetime.datetime(2017, 1, 20, 0, 0), 'SR705', 7009.0, 7025.0, 6779.0, 6880.0, 635874.0, 4394029.16,
             7219.0, 6663.0],
            [datetime.datetime(2017, 1, 23, 0, 0), 'SR705', 6883.0, 6942.0, 6869.0, 6917.0, 232382.0, 1603798.03,
             7187.0, 6633.0],
            [datetime.datetime(2017, 1, 24, 0, 0), 'SR705', 6927.0, 6988.0, 6908.0, 6954.0, 271098.0, 1884149.1, 7179.0,
             6625.0],
            [datetime.datetime(2017, 1, 25, 0, 0), 'SR705', 6971.0, 6978.0, 6921.0, 6956.0, 150678.0, 1047570.91,
             7228.0, 6672.0],
            [datetime.datetime(2017, 1, 26, 0, 0), 'SR705', 6965.0, 7020.0, 6930.0, 6933.0, 190906.0, 1328731.62,
             7439.0, 6465.0], ]

        cls.table = CacheClient.DailyTable()
        cls.table.create()

    def tearDown(self):
        self.table.clear()

    @classmethod
    def tearDownClass(cls):
        Conf.get_gta_db(CacheClient.DB_TYPE.SQLITE, True)
        os.remove(Conf.CACHE_DB_PATH)

    def test_insert(self):
        self.table.insert(self.data)
        self.assertListEqual(self.data, self.table.select('SR705', self.table.fields, datetime.datetime(2016, 12, 30), datetime.datetime(2017, 1, 27)))


class TestCacheClient(unittest.TestCase):
    def setUp(self):
        self.client = CacheClient.CacheDataClient()
        self.client.add_client(CacheClient.AdapterClient())

    def tearDown(self):
        Conf.get_gta_db(CacheClient.DB_TYPE.SQLITE, clear=True)
        os.remove(Conf.CACHE_DB_PATH)

    def test_daily(self):
        conf = {
            'dataName': 'data',
            'code': 'ag1701',
            'start': datetime.datetime(2016, 12, 1),
            'end': datetime.datetime(2016, 12, 15),
            'fields': 'open,close,high,amt,limitup'
        }
        l = self.client.get_data(copy.deepcopy(conf))
        self.assertEqual(l[0][0], datetime.datetime(2016, 12, 1))
        self.assertEqual(l[-1][0], datetime.datetime(2016, 12, 14))

        c = copy.deepcopy(conf)
        c.update({'start': datetime.datetime(2016, 12, 20), 'end': datetime.datetime(2017, 1, 7)})
        l = self.client.get_data(c)
        self.assertEqual(l[0][0], datetime.datetime(2016, 12, 20))
        self.assertEqual(l[-1][0], datetime.datetime(2017, 1, 6))

        c = copy.deepcopy(conf)
        c.update({'start': datetime.datetime(2016, 11, 10, 0, 0, 1), 'end': datetime.datetime(2016, 11, 21, 0, 0, 1)})
        l = self.client.get_data(c)
        self.assertEqual(l[0][0], datetime.datetime(2016, 11, 11))
        self.assertEqual(l[-1][0], datetime.datetime(2016, 11, 21))

        c = copy.deepcopy(conf)
        c.update({'start': datetime.datetime(2016, 11, 17), 'end': datetime.datetime(2017, 1, 10)})
        l1 = self.client.get_data(c)
        self.assertEqual(l1[0][0], datetime.datetime(2016, 11, 17))
        self.assertEqual(l1[-1][0], datetime.datetime(2017, 1, 9))

        c.update({'start': datetime.datetime(2016, 11, 17), 'end': datetime.datetime(2017, 1, 10)})
        l2 = self.client.get_data(c)

        self.assertListEqual(l1, l2)
