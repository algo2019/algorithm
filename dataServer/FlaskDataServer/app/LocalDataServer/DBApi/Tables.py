import datetime

import sys

from DBServer.BaseTable import Table
from DBServer.SqliteServer import Server
import Conf
import tools
from dataServer import Conf as DS_CONF
DS_CONF.DB_PATH = None

MaxGetDataErrTry = 5


class DomInfoTable(Table):
    start = '2000-01-01'
    end = None

    def __init__(self):
        super(DomInfoTable, self).__init__('DomInfoTable')
        self.trading_table = TradingDateTable()
        self.symbols = set()
        for key in Conf.EXCHANGE_ID:
            self.symbols = self.symbols | Conf.EXCHANGE_ID[key]

    def get_db(self):
        return Server(Conf.DB_PATH)

    def open(self):
        self.trading_table.open()
        self._db.open()

    def close(self):
        self.trading_table.close()
        self._db.close()

    def create(self):
        sql = '''create table %s (
            symbol TEXT PRIMARY KEY,
            symbolcode TEXT,
            startdate TEXT,
            enddate TEXT
        )''' % self.name
        self._db.execute(sql)
        self._db.commit()

    def init_data(self):
        if self.exists():
            print 'DomInfoTable: use old table\ninit break!'
        else:
            print 'DomInfoTable: create new table'
            self.create()
            print 'DomInfoTable: start to init data'
            self._insert(self._get_data(self.start))
            print 'DomInfoTable: init data ready'

    def _get_data(self, start):
        from dataServer import dataServer
        d = dataServer()
        d.start()
        print 'DomInfoTable: get data from {} to {} of symbols {}'.format(start, self.end, len(self.symbols))
        conf = {
            'dataName': 'domInfo',
            'start': start,
            'end': self.end,
            'afterday': 0,
            'beforday': 0,
            'commodity': list(self.symbols),
        }
        rt = d.wmm(conf)
        d.stop()
        return rt

    def _insert(self, data):
        print 'DomInfoTable: insert data {}'.format(len(data))
        if len(data) != 0:
            sql = 'insert into {} (symbol,symbolcode,startdate,enddate) values'.format(self.name)
            values = ["','".join((line[0],
                                  tools.get_symbol(line[0]),
                                  str(tools.format_to_datetime(line[1], time=False)),
                                  str(tools.format_to_datetime(line[2], time=False)))) for line in data]

            i = 0
            while i < len(values):
                self._db.execute(sql + "('" + "'),('".join(values[i:i + 500]) + "')")
                i += 500
            self._db.commit()

    def select(self, symbol_or_instrument, start, end, before=0, after=0):
        start = str(tools.format_to_datetime(start, time=False))
        end = str(tools.format_to_datetime(end, time=False))
        sql = '''select symbol,startdate,enddate from {tn}
        where symbolcode='{sc}' and ((startdate>='{s}' and startdate<'{e}') or
        (enddate>'{s}' and enddate<='{e}') or (startdate<'{s}' and enddate>'{e}')) '''.format(
            tn=self.name, sc=tools.get_symbol(symbol_or_instrument), s=start, e=end)
        self._db.execute(sql)
        return self._format_rt(self._db.fetchall(), start, end, before, after)

    def _format_rt(self, data, start='0', end='Z', before=0, after=0):
        return [[str(line[0]),
                 self.trading_table.tdaysoffset(before, max(line[1], start)),
                 self.trading_table.tdaysoffset(0 - after, min(line[2], end))] for line in data]

    def select_symbol(self, symbol, before=0, after=0):
        sql = 'select symbol,startdate,enddate from {} where symbol = ?'.format(self.name)
        self._db.execute(sql, (symbol,))
        return self._format_rt(self._db.fetchall(), before=before, after=after)

    def _delete_symbol(self, symbol):
        sql = 'delete from {} where symbol = ?'.format(self.name)
        self._db.execute(sql, (symbol,))
        self._db.commit()

    def update(self):
        sql = 'select max(enddate) from {}'.format(self.name)
        self._db.execute(sql)
        last_date = self._db.fetchone()[0]
        data = self._get_data(last_date)
        print 'DomInfoTable : need to update {}'.format(len(data))
        for i in xrange(len(data)):
            if str(tools.format_to_datetime(data[i][1], time=False)) == last_date:
                old = self.select_symbol(data[i][0])
                if len(old) > 0:
                    data[i][1] = old[0][1]
                    data[i][2] = str(tools.format_to_datetime(data[i][2], time=False))
                    self._delete_symbol(old[0][0])
        self._insert(data)
        print 'DomInfoTable : update ready!'
        return last_date


class DailyDataTable(Table):
    start = None
    end = None

    def __init__(self):
        super(DailyDataTable, self).__init__('DailyDataTable')

    def open(self):
        self._db.open()

    def close(self):
        self._db.close()

    def get_db(self):
        return Server(Conf.DB_PATH)

    def create(self):
        sql = '''create table %s (
            date TEXT,
            symbol TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INT,
            amt REAL,
            avg REAL,
            limitup REAL,
            limitdown REAL,
            PRIMARY KEY(date, symbol)
        )''' % self.name
        self._db.execute(sql)
        self._db.commit()

    def init_data(self):
        if self.exists():
            print 'DailyDataTable : use old table'
        else:
            print 'DailyDataTable : create new table'
            self.create()

        print 'DailyDataTable : get all dom info'
        dom_table = DomInfoTable()
        dom_sql = 'select * from {}'.format(dom_table.name)
        tdt = TradingDateTable()
        tdt.open()
        print 'DailyDataTable : insert into table ...'
        for symbol, symbolcode, startdate, enddate in self.run_sqls(dom_sql):
            startdate, enddate = tdt.tdaysoffset(30, startdate), tdt.tdaysoffset(-30, enddate)
            if len(self.select(symbol, startdate, enddate)) == 0:
                self._insert_data(self._get_data(symbol, startdate, enddate))
        print '\nDailyDataTable : insert over'
        tdt.close()

    def _get_data(self, symbol, start, end):
        start = self.start or start
        end = self.end or end
        if tools.format_to_datetime(end) > datetime.datetime.now():
            end = datetime.datetime.now()
        print 'DailyDataTable : get data {} {} {}'.format(symbol, start, end)
        from dataServer import dataServer
        for _ in xrange(MaxGetDataErrTry):
            try:
                d = dataServer()
                d.start()
                conf = {
                    'dataName': 'data',
                    'start': start,
                    'end': end,
                    'code': symbol,
                    'includeend': True,
                    'fields': 'open,high,low,close,volume,AMOUNT,AVGPRICE,limitup,limitdown',
                    'period': '1d',
                }
                res = d.wmm(conf)
                d.stop()
                return res
            except Exception as e:
                print e
                print 'get data err! retrying . . .'
        raise Exception('get data retry to max')

    def _insert_data(self, data):
        print 'DailyDataTable : insert data', len(data)
        sql = 'insert into {} (date, symbol, open, high, low, close, volume, amt, avg, limitup, limitdown) values'.format(
            self.name)
        values = []
        for dt, ins, open, high, low, close, volume, amt, avg, limitup, limitdown in data:
            values.append(
                "','".join(map(str, (dt.date(), ins, open, high, low, close, volume, amt, avg, limitup, limitdown))))
        i = 0
        while i < len(values):
            self._db.execute(sql + "('" + "'),('".join(values[i:i + 500]) + "')")
            i += 500
        self._db.commit()

    def update(self, update_date=None):
        print 'DailyDataTable : start to update'
        tdt = TradingDateTable()
        tdt.open()
        if update_date is None:
            last_date_sql = "select max(date) from {}".format(self.name)
            self._db.execute(last_date_sql)
            update_date = tdt.tdaysoffset(-1, self._db.fetchone()[0])

        print 'DailyDataTable : update date', update_date
        dom_table = DomInfoTable()
        print 'DailyDataTable : get dom info'
        dom_sql = "select * from {} where enddate >= '{}'".format(dom_table.name, tdt.tdaysoffset(10, update_date))
        print 'DailyDataTable : insert into table ...'
        last_ins_date_sql = "select max(date) from {} where symbol = ?".format(self.name)
        for symbol, symbolcode, startdate, enddate in self.run_sqls(dom_sql):
            res = self.run_sqls(last_ins_date_sql, (symbol, ))[0][0]
            if res is None:
                start = tdt.tdaysoffset(30, startdate)
            else:
                start = tdt.tdaysoffset(-1, res)
            end = tdt.tdaysoffset(-30, enddate)
            print 'DailyDataTable : update', symbol, start, end
            self._insert_data(self._get_data(symbol, start, end))
        print 'DailyDataTable : insert over'
        tdt.close()

    def select(self, symbol, start, end, fields=None):
        fields = fields or 'open,high,low,close,volume,amt,avg,limitup,limitdown'
        old_symbol = str(symbol)
        symbol = symbol.upper()
        sql = "select date,{} from {} where symbol = ? and date >= ? and date < ?".format(fields, self.name)
        self._db.execute(sql, (
            symbol, tools.format_to_datetime(start, time=False), tools.format_to_datetime(end, time=False)))
        rt = []
        for line in self._db.fetchall():
            rt.append([tools.format_to_datetime(line[0]), old_symbol] + list(line[1:]))
        return rt


class _MinDataTable(Table):
    def __init__(self, name, db):
        self.__db = db
        super(_MinDataTable, self).__init__(name)

    def get_db(self):
        return self.__db

    def open(self):
        pass

    def close(self):
        pass

    def create(self):
        sql = '''create table %s (
            date TEXT,
            time TEXT,
            symbol TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INT,
            amt REAL,
            openints INT,
            chg REAL,
            chg_pct REAL,
            PRIMARY KEY(date, time, symbol)
        )''' % self.name
        self._db.execute(sql)
        self._db.commit()


class MinDataTable(object):
    start = '2010-01-01'
    end = None
    periods = ['1m', '5m', '10m', '15m']

    def __init__(self):
        self._db = Server(Conf.DB_PATH)

    def open(self):
        self._db.open()

    def close(self):
        self._db.close()

    @staticmethod
    def _get_table_name(symbol, period):
        return 'MinDataTable_{}_{}'.format(tools.get_symbol(symbol), period)

    def init_data(self, reset=False, check=False, exchange_id=None):
        print 'MinDataTable : get all dom info'
        dom_table = DomInfoTable()
        dom_sql = 'select * from {} order by symbolcode'.format(dom_table.name)
        tdt = TradingDateTable()
        tdt.open()
        t = set()

        if reset:
            sys.stderr.write('MinDataTable : work in reset model!\n')
        elif check:
            sys.stderr.write('MinDataTable : work in check model!\n')

        for period in self.periods:
            print 'MinDataTable : insert period {} into table ...'.format(period)
            for symbol, symbolcode, startdate, enddate in tdt.run_sqls(dom_sql):
                if exchange_id and tools.get_exchange_id(symbolcode) != exchange_id:
                    continue
                if enddate < self.start:
                    continue
                if startdate < self.start:
                    startdate = self.start

                table = _MinDataTable(self._get_table_name(symbolcode, period), self._db)

                if reset and symbolcode + period not in t:
                    sys.stderr.write('MinDataTable : reset table of {} {}\n'.format(symbolcode, period))
                    table.drop()
                    t.add(symbolcode + period)

                if not table.exists():
                    table.create()
                    print 'MinDataTable : create new table of', symbolcode, period
                m_start = tdt.tdaysoffset(30, startdate)
                if m_start < self.start:
                    m_start = self.start

                m_end = tdt.tdaysoffset(-30, enddate)
                if check:
                    sys.stderr.write('MinDataTable : checking {} {}\n'.format(symbol, period))
                    cf = False
                    ts = startdate
                    while ts < enddate:
                        if not len(self.select(symbol, period, ts, tdt.tdaysoffset(-1, ts))):
                            cf = True
                            break
                        ts = tdt.tdaysoffset(-10, ts)
                    if not cf and not len(self.select(symbol, period, enddate, tdt.tdaysoffset(-1, enddate))):
                        cf = True
                    if cf:
                        sys.stderr.write('MinDataTable : checkout of {} {}\n'.format(symbol, period))
                        self.delete_symbol(symbol, period)

                if len(self.select(symbol, period, startdate, tdt.tdaysoffset(-1, startdate))) == 0:
                    try:
                        self._insert_data(symbol, period, self._get_data(symbol, period, m_start, m_end))
                    except Exception as e:
                        sys.stderr.writelines('MinDataTable : {} insert err: {}\n'.format(symbol, str(e)))
                else:
                    print 'pass', symbol
            print '\nMinDataTable : insert over'
        tdt.close()

    def delete_symbol(self, symbol, period):
        sql = 'delete from {} where symbol = ?'.format(self._get_table_name(symbol, period))
        self._db.execute(sql, (symbol,))

    def _get_data(self, symbol, period, start, end, tradingday=True, includeend=None):
        if tools.format_to_datetime(end) > datetime.datetime.now():
            end = datetime.datetime.now()
        print 'MinDataTable : get data {} {} {} {}'.format(symbol, period, start, end)
        if tools.get_exchange_id(symbol) == 'CFFEX':
            fields = 'open,high,low,close,volume,amt,volume,MINTQ,MINTM'
        else:
            fields = 'open,high,low,close,volume,amt,OPENINTS,CHGMIN,CHGPCTMIN'
        from dataServer import dataServer
        for _ in xrange(MaxGetDataErrTry):
            try:
                d = dataServer()
                d.start()
                conf = {
                    'dataName': 'data',
                    'start': start,
                    'end': end,
                    'code': symbol,
                    'includeend': includeend or tradingday,
                    'tradingday': tradingday,
                    'fields': fields,
                    'period': period,
                }
                res = d.wmm(conf)
                d.stop()
                return res
            except Exception as e:
                print e
                print 'get data err! retrying'
        raise Exception('get data retry to max')

    def _insert_data(self, symbol, period, data):
        print 'MinDataTable : insert data {}'.format(len(data))
        sql = 'insert into {} (date,time,symbol,open,high,low,close,volume,amt,openints,chg,chg_pct) values'.format(
            self._get_table_name(symbol, period))
        values = []
        for dt, ins, open, high, low, close, volume, amt, openints, chg, chg_pct in data:
            values.append(
                "','".join(map(str, (
                    dt.date(), dt.time(), ins, open, high, low, close, volume, amt, openints, chg, chg_pct))))
        i = 0
        while i < len(values):
            self._db.execute(sql + "('" + "'),('".join(values[i:i + 500]) + "')")
            i += 500
        self._db.commit()

    def update(self, update_date=None):
        print 'MinDataTable : start to update'
        tdt = TradingDateTable()
        tdt.open()
        if update_date is None:
            last_date_sql = "select max(date) from {}".format(self._get_table_name('ag', '15m'))
            self._db.execute(last_date_sql)
            update_date = tdt.tdaysoffset(-1, self._db.fetchone()[0])
        update_date = tdt.tdaysoffset(10, update_date)
        print 'MinDataTable : update date', update_date
        dom_table = DomInfoTable()
        print 'MinDataTable : get dom info'
        dom_sql = "select * from {} where enddate >= '{}'".format(dom_table.name, update_date)
        last_ins_date_sql = "select date,time from {} where symbol = ? and date >= ? order by date,time"
        for symbol, symbolcode, startdate, enddate in tdt.run_sqls(dom_sql):
            for period in self.periods:
                print 'MinDataTable : update {} into table ...'.format(period)
                res = tdt.run_sqls(last_ins_date_sql.format(self._get_table_name(symbol, period)), (symbol, tdt.tdaysoffset(20, update_date)))
                if len(res) is 0:
                    start = tdt.tdaysoffset(30, startdate)
                else:
                    start = tools.format_to_datetime(' '.join(res[-1])) + datetime.timedelta(minutes=1)
                end = tdt.tdaysoffset(-30, enddate)
                print 'MinDataTable : update', symbol, start, end
                self._insert_data(symbol, period, self._get_data(symbol, period, start, end, tradingday=False))

        print 'MinDataTable : insert over'
        tdt.close()

    def select(self, symbol, period, _start, _end, fields=None):
        fields = fields or 'open,high,low,close,volume,amt'
        old_symbol = str(symbol)
        symbol = symbol.upper()
        table_name = self._get_table_name(symbol, period)
        start = tools.format_to_datetime(_start)
        end = tools.format_to_datetime(_end)
        if type(fields) not in {str, unicode}:
            fields = ','.join(fields)
        sql = "select date,time,{} from {} where symbol=? and(date>? or(date=? and time>=?))and(date<? or(date=? and time<?))order by date,time".format(
            fields, table_name)
        self._db.execute(sql, (
            symbol, str(start.date()), str(start.date()), str(start.time()), str(end.date()), str(end.date()),
            str(end.time())))
        rt = []
        for line in self._db.fetchall():
            rt.append([tools.format_to_datetime('{} {}'.format(line[0], line[1])), old_symbol] + list(line[2:]))
        return rt


class TradingDateTable(Table):
    start = '2000-01-01'
    end = '2020-01-01'

    def __init__(self):
        super(TradingDateTable, self).__init__('TradingDataTable')

    def open(self):
        self._db.open()

    def close(self):
        self._db.close()

    def get_db(self):
        return Server(Conf.DB_PATH)

    def create(self):
        sql = '''create table %s (
            date TEXT PRIMARY KEY
        )''' % self.name
        self._db.execute(sql)
        self._db.commit()

    def init_data(self):
        print 'TradingDateTable : start init data from {} to {}'.format(self.start, self.end)
        if self.exists():
            print 'TradingDateTable : use old table\ninit break'
        else:
            print 'TradingDateTable : create new table'
            self.create()
            sql = 'insert into {} (date) values'.format(self.name)
            from dataServer import dataServer
            d = dataServer()
            d.start()
            res = d.tdays(self.start, self.end)
            d.stop()
            print 'TradingDateTable : start insert to table'
            values = [str(i.date()) for i in res.Data[0]]
            i = 0
            while i < len(values):
                self._db.execute(sql + "('" + "'),('".join(values[i:i + 500]) + "')")
                i += 500
            self._db.commit()
            print 'TradingDateTable : init data ready'

    def tdays(self, start, end):
        start = tools.format_to_datetime(start, time=False)
        end = tools.format_to_datetime(end, time=False)
        sql = 'select date from {} where date >= ? and date < ?'.format(self.name)
        self._db.execute(sql, (start, end))
        return [str(i[0]) for i in self._db.fetchall()]

    def tdaysoffset(self, offset, start):
        _len = max(offset, 10)
        forword = True
        if offset < 0:
            forword = False
            offset = abs(offset)
        start = tools.format_to_datetime(start)
        while 1:
            _len += _len
            if forword:
                res = self.tdays(start - datetime.timedelta(days=_len), start + datetime.timedelta(days=1))
            else:
                res = self.tdays(start, start + datetime.timedelta(days=_len))
            if len(res) > offset:
                if forword:
                    return res[-1 - offset]
                else:
                    return res[offset]
