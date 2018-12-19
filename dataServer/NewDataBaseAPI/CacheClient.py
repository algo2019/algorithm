import copy

import datetime

from Client import ControlClient, BaseClient
from Conf import get_gta_db, DB_TYPE
from interval import Interval, IntervalSet
from tools import format_to_datetime as dt_format
from Common.CommonLogServer.mlogging import get_logger


def exists_table(db, table):
    one = db.execute("select count(*) c from sqlite_master where type=? and name=?", ['table', table]).fetchone()
    if one[0] > 0:
        return True
    return False


def drop_table(db, table):
    db.execute("drop table %s" % table)
    db.commit()


class UpdateTable(object):
    def __init__(self):
        self.__name = 'update_info'
        self._logger = get_logger('UpdateTable', 'DataService')

    @property
    def name(self):
        return self.__name

    def init_db(self):
        db = get_gta_db(DB_TYPE.SQLITE)
        if not exists_table(db, self.name):
            self.create()

    def create(self):
        db = get_gta_db(DB_TYPE.SQLITE)
        sql = '''create table %s (
                    code TEXT NOT NULL COLLATE NOCASE,
                    period TEXT NOT NULL,
                    start TEXT NOT NULL,
                    end TEXT NOT NULL,
                    PRIMARY KEY(code, period, start)
                )''' % self.name
        db.execute(sql)
        db.commit()

    def get_db_interval_sets(self, code, period):
        sql = "select start,end from {} where code = ? and period = ? order by start".format(self.name)
        db = get_gta_db(DB_TYPE.SQLITE)
        return self.list_to_interval_sets(db.execute(sql, (code, period)).fetchall())

    @staticmethod
    def interval_sets_to_list(sets):
        return [[c.lower_bound, c.upper_bound] for c in sets]

    @staticmethod
    def list_to_interval_sets(lists):
        return IntervalSet([Interval(str(s), str(e), upper_closed=False) for s, e in lists])

    def get_update_interval(self, conf):
        start = dt_format(conf['start'], ms=False)
        end = dt_format(conf['end'], ms=False)
        exists_set = self.get_db_interval_sets(conf['code'], conf['period'])
        rt = self.interval_sets_to_list(IntervalSet([Interval(str(start), str(end), upper_closed=False)]) - exists_set)
        return map(lambda y: map(lambda x: dt_format(x, ms=False), y), rt)

    def _delete(self, code, period):
        sql = "delete from {} where code = ? and period = ?".format(self.name)
        db = get_gta_db(DB_TYPE.SQLITE)
        db.execute(sql, (code, period))
        db.commit()

    def _insert(self, code, period, lists):
        if not len(lists):
            return
        sql = "insert into {} (code,period,start,end)values(".format(self.name) + "),(".join(
            ["'{}','{}','{}','{}'".format(code, period, l[0], l[1]) for l in lists]) + ")"
        db = get_gta_db(DB_TYPE.SQLITE)
        db.execute(sql)
        db.commit()

    def clear(self):
        sql = "delete from {}".format(self.name)
        db = get_gta_db(DB_TYPE.SQLITE)
        db.execute(sql)
        db.commit()

    def update_interval(self, code, period, range_lists):
        if not len(range_lists):
            return
        new = self.interval_sets_to_list(
            self.get_db_interval_sets(code, period) + self.list_to_interval_sets(range_lists))
        self._delete(code, period)
        self._insert(code, period, map(lambda y: map(lambda x: dt_format(x, ms=False), y), new))
        for s, e in new:
            self._logger.debug('{} {} {} -> {}'.format(code, period, s, e))


class DailyTable(object):
    __fields_str = 'open,close,high,low,volume,amt,limitup,limitdown'

    def __init__(self):
        self.__name = 'daily'
        self.__fields = set(self.__fields_str.split(','))

    @property
    def name(self):
        return self.__name

    @property
    def fields_set(self):
        return self.__fields

    @property
    def fields(self):
        return self.__fields_str

    def create(self):
        db = get_gta_db(DB_TYPE.SQLITE)
        sql = '''create table %s (
                    date TEXT NOT NULL,
                    code TEXT NOT NULL COLLATE NOCASE,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INT NOT NULL,
                    amt REAL NOT NULL,
                    limitup REAL NOT NULL,
                    limitdown REAL NOT NULL,
                    PRIMARY KEY(date, code)
                )''' % self.name
        db.execute(sql)
        db.commit()

    def clear(self):
        sql = "delete from {}".format(self.name)
        db = get_gta_db(DB_TYPE.SQLITE)
        db.execute(sql)
        db.commit()

    def insert(self, lists):
        if len(lists) == 0:
            return
        sql = "insert into {} (date,code,{})values".format(self.name, self.fields) + ",".join(
            ["('{} 00:00:00','{}')".format(l[0].date(), "','".join(map(str, l[1:]))) for l in lists])
        db = get_gta_db(DB_TYPE.SQLITE)
        db.execute(sql)
        db.commit()

    def select(self, code, fields, start, end):
        sql = "select date,code,{} from {} where code = ? and date >= ? and date < ? order by date".format(fields,
                                                                                                           self.name)
        db = get_gta_db(DB_TYPE.SQLITE)
        return map(lambda x: [dt_format(x[0])] + list(x)[1:],
                   db.execute(sql, (code, start, end)).fetchall())


class MinTable(object):
    __fields_str = 'open,close,high,low,volume,amt'

    def __init__(self):
        self.__name = 'min_table'
        self.__fields = set(self.__fields_str.split(','))

    @property
    def name(self):
        return self.__name

    @property
    def fields_set(self):
        return self.__fields

    @property
    def fields(self):
        return self.__fields_str

    def create(self):
        db = get_gta_db(DB_TYPE.SQLITE)
        sql = '''create table %s (
                       date TEXT NOT NULL,
                       code TEXT NOT NULL COLLATE NOCASE,
                       period TEXT NOT NULL,
                       open REAL NOT NULL,
                       high REAL NOT NULL,
                       low REAL NOT NULL,
                       close REAL NOT NULL,
                       volume INT NOT NULL,
                       amt REAL NOT NULL,
                       PRIMARY KEY(date, code)
                   )''' % self.name
        db.execute(sql)
        db.commit()

    def clear(self):
        sql = "delete from {}".format(self.name)
        db = get_gta_db(DB_TYPE.SQLITE)
        db.execute(sql)
        db.commit()

    def insert(self, lists):
        if len(lists) == 0:
            return
        sql = "insert into {} (date,code,{})values".format(self.name, self.fields) + ",".join(
            ["('{} 00:00:00','{}')".format(l[0].date(), "','".join(map(str, l[1:]))) for l in lists])
        db = get_gta_db(DB_TYPE.SQLITE)
        db.execute(sql)
        db.commit()

    def select(self, code, period, fields, start, end):
        sql = "select date,code,{} from {} where code = ? and period = ? and date >= ? and date < ? order by date".format(
            fields, self.name)
        db = get_gta_db(DB_TYPE.SQLITE)
        return map(lambda x: [dt_format(x[0])] + list(x)[1:],
                   db.execute(sql, (code, period, start, end)).fetchall())


class CacheDataClient(ControlClient):
    def __init__(self):
        self._adapter_client = None
        self._update_table = UpdateTable()
        self._daily_table = DailyTable()
        self._min_table = MinTable()
        self._logger = get_logger('CacheDataClient', 'DataService')
        self.init_table()

    def init_table(self):
        db = get_gta_db(DB_TYPE.SQLITE)
        for table in [self._update_table, self._daily_table]:
            if not exists_table(db, table.name):
                table.create()

    def add_client(self, adapter_client):
        self._adapter_client = adapter_client

    def remove_client(self, *args, **kwargs):
        self._adapter_client = None

    def get_data(self, conf):
        self._logger.debug('dataName: {}'.format(conf['dataName']))
        if conf['dataName'] != 'data':
            return self._adapter_client.get_data(conf)
        if conf.get('period') is None:
            conf['period'] = '1d'
        if conf['period'] == '1d':
            return self.get_daily(conf)
        else:
            return self.get_min(conf)

    def get_daily(self, conf):
        self._logger.debug('daily: {} {} -> {}'.format(conf['code'], conf['start'], conf['end']))
        update_lists = self._update_table.get_update_interval(conf)
        t_conf = copy.deepcopy(conf)
        for line in update_lists:
            t_conf.update(
                {'start': line[0], 'end': line[1], 'fields': 'open,close,high,low,volume,amt,limitup,limitdown'})
            data = self._adapter_client.get_data(t_conf)
            if len(data) > 0:
                now = datetime.datetime.now()
                if line[1].date() >= now.date():
                    if data[-1][0].date() == now.date():
                        line[1] = now
                    else:
                        line[1] = now.replace(hour=0, minute=0, second=0, microsecond=0)
                self._daily_table.insert(data)
            self._logger.debug('insert into local: {} | {} -> {}'.format(len(data), line[0], line[1]))
        self._update_table.update_interval(conf['code'], '1d', update_lists)
        return self._daily_table.select(conf['code'], conf['fields'], conf['start'], conf['end'])

    def get_min(self, conf):
        self._logger.debug('min: {} {} {} -> {}'.format(conf['code'], conf['period'], conf['start'], conf['end']))
        update_lists = self._update_table.get_update_interval(conf)
        t_conf = copy.deepcopy(conf)
        for line in update_lists:
            t_conf.update({'start': line[0], 'end': line[1], 'fields': 'open,close,high,low,volume,amt'})
            data = self._adapter_client.get_data(t_conf)
            if len(data) > 0:
                now = datetime.datetime.now()
                if line[1] >= now:
                    line[1] = now - datetime.timedelta(minutes=10)
                self._min_table.insert(data)
            self._logger.debug('insert into local: {} | {} -> {}'.format(len(data), line[0], line[1]))
        self._update_table.update_interval(conf['code'], conf['period'], update_lists)
        return self._min_table.select(conf['code'], conf['period'], conf['fields'], conf['start'], conf['end'])


class AdapterClient(BaseClient):
    def __init__(self):
        from dataBaseAPI.dataBaseClient import Client
        self._client = Client()

    def get_data(self, conf):
        self._client.start()
        rt = self._client.wmm(conf)
        self._client.stop()
        return rt
