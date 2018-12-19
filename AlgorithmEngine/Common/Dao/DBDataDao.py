import MySqlDao
import datetime
from tools import format_to_datetime as df


class DBDataDao(MySqlDao.MySqlDao):
    fields_table = {
        'open': 'openprice',
        'high': 'highprice',
        'low': 'lowprice',
        'close': 'closeprice'
    }

    def __init__(self):
        super(DBDataDao, self).__init__()

    def create(self):
        sql = '''CREATE TABLE IF NOT EXISTS MainContract (
                    SYMBOL varchar(4) not null,
                    TDATE date not null,
                    CODE varchar(8) null,
                    EXCHANGEID varchar(6) null,
                    PRIMARY KEY (SYMBOL, TDATE)
                );
                CREATE TABLE IF NOT EXISTS DayData(
                    CODE varchar(10) not null,
                    TDATE date not null,
                    OPENPRICE decimal(10,3) null,
                    HIGHPRICE decimal(10,3) null,
                    LOWPRICE decimal(10,3) null,
                    CLOSEPRICE decimal(10,3) null,
                    PERCLOSEPRICE decimal(10,3) null,
                    AVGPRICE decimal(10,3) null,
                    SETTLEPRICE decimal(10,3) null,
                    PERSETTLEPRICE decimal(10,3) null,
                    VOLUME decimal(20) null,
                    AMOUNT decimal(20,3) null,
                    LIMITUP decimal(10,3) null,
                    LIMITDOWN decimal(10,3) null,
                    OPENINTERPRIST decimal null,
                    CHG decimal(10,3) null,
                    CHGRT float(5,3) null,
                    UPDATETIME datetime null,
                    EXCHANGEID varchar(10) null,
                    primary key (CODE, TDATE)
                );
                CREATE TABLE IF NOT EXISTS TradingDay (
                    TDATE date not null
                        primary key
                );'''
        self.run_sqls(sql)

    def tdays(self, start, end=None):
        sql = '''SELECT TDATE FROM TradingDay WHERE TDATE >= '{}' and TDATE <= '{}' '''.format(
            df(start, time=False), df(end or datetime.datetime.now(), time=False))
        return map(lambda x: x[0], self.run_sqls(sql))

    def tdaysoffset(self, offset, dt=None):
        _len = max(offset, 10)
        foreword = True
        if offset < 0:
            foreword = False
            offset = abs(offset)
        last_len = 0
        start = df(dt or datetime.datetime.now(), time=False)

        while 1:
            _len += _len
            if foreword:
                res = self.tdays(start - datetime.timedelta(days=_len), start)
            else:
                res = self.tdays(start, start + datetime.timedelta(days=_len))

            if len(res) == last_len:
                return res
            last_len = len(res)
            if len(res) > offset:
                if foreword:
                    date = res[-1 - offset]
                else:
                    date = res[offset]
                return date

    def main_contract(self, symbol, start, end, before=0, after=0):
        start = self.tdaysoffset(before, start)
        end = self.tdaysoffset(0-after, end)
        sql = '''SELECT CODE,TDATE FROM MainContract WHERE SYMBOL = '{}' and TDATE >= '{}' and TDATE <= '{}' ORDER BY TDATE'''.format(
            symbol, start, end
        )
        res = []
        last = None
        dt_last = None
        start = None
        for c, d in self.run_sqls(sql):
            if last is None:
                last = c
                start = d
            elif last < c:
                res.append((last, symbol, start, dt_last))
                last, start = c, d
            else:
                pass
            dt_last = d
        if last != None:
            res.append((last, symbol, start, dt_last))
        return res

    def add_trading_day(self, dt):
        sql = '''INSERT INTO  TradingDay VALUES ('{}')'''.format(dt)
        return self.run_sqls(sql, False)

    def _common_fields(self, fields):
        if type(fields) != list:
            fields = fields.split(',')
        return ','.join([self.fields_table.get(x, x) for x in fields])

    def day(self, code, start, end, fields=None):
        if fields is None or fields == '':
            fields = 'openprice,highprice,lowprice,closeprice,volume'
        else:
            fields = self._common_fields(fields)

        sql = '''SELECT TDATE,CODE,{} FROM DayData WHERE CODE = '{}' and TDATE >= '{}' and TDATE <= '{}' ORDER BY TDATE'''.format(
            fields, code, start, end
        )
        return self.run_sqls(sql)

    def is_trading_day(self, dt=None):
        sql = '''SELECT TDATE FROM TradingDay WHERE TDATE = '{}' '''.format(df(dt or datetime.datetime.now(), time=False))
        return True if len(self.run_sqls(sql)) > 0 else False

