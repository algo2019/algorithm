import pyodbc

import datetime
from tools import format_to_datetime as format_dt
from dataServer import Conf
from dataServer import dataServer

Conf.CACHE = False

d = dataServer()


def get_table(period, date_time):
    return "MFL1_TRDMIN{:0>2}_{}".format(period, date_time.strftime('%Y%m'))


def get_db(date_time):
    return 'GTA_MFL1_TRDMIN_{}'.format(date_time.strftime('%Y%m'))


def get_data(ins, start, end):
    d.start()
    conf = {
        'dataName': 'data',
        'code': ins,
        'fields': 'close,open,high,low,oi,volume,amt',
        'start': start,
        'end': end,
        'period': '1m',
    }
    res = d.wmm(conf)
    d.stop()
    return res


def get_all_instruments(start, end):
    print 'get all instrument of', start, end
    d.start()
    conf = {
        'dataName': 'sql',
        'sql': "select SYMBOL from FUT_QUOTATIONHISTORY where TRADINGDATE>='{}' and TRADINGDATE<='{}' group by SYMBOL;".format(d.tdaysoffset(0, start.date()).Data[0][0], d.tdaysoffset(0, end.date()).Data[0][0])
    }
    print conf
    rt = d.wmm(conf)
    d.stop()
    return [str(i[0]) for i in rt]


class DBOper(object):
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.db_dt = None

    def connect(self, date_time):
        self.conn = pyodbc.connect(
            "DRIVER={{SQL Server}};SERVER=10.4.27.179;port=1433;UID=gta_updata;PWD=rI2016;DATABASE={};TDS_Version=8.0" \
                .format(get_db(date_time)))
        self.cursor = self.conn.cursor()

    def get_cursor(self, date_time):
        if self.db_dt is None:
            self.db_dt = date_time
            self.connect(date_time)
            return self.cursor
        elif date_time.strftime('%Y%m') == self.db_dt.strftime('%Y%m'):
            return self.cursor
        else:
            self.cursor.close()
            self.conn.close()
            self.db_dt = date_time
            self.connect(date_time)
            return self.cursor

    def close(self):
        self.cursor.close()
        self.conn.close()

    def insert(self, period, datas):
        ln = 'CONTRACTID, TDATETIME, OPENPX, HIGHPX, LOWPX, LASTPX, MINQTY, TURNOVER, OPENINTS, CHGMIN, CHGPCTMIN, VARIETIES, MFLXID, MARKET, UNIX'
        inserts = []
        dt, instrument = datas[0][:2]
        sql = 'insert into {}({})values'.format(get_table(period, dt), ln)
        cursor = self.get_cursor(dt)
        print dt, instrument,

        for line in datas:
            dt, instrument, opn, cls, hi, lw, chg, chgpct, oi, mq, mt = line
            inserts.append(
                "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{:.4f}', '-', '-', '-', '0')".format(
                    instrument, str(dt)[:19], opn, hi, lw, cls, mq, mt, oi, chg, chgpct))
        print len(inserts)
        if len(inserts) != 0:
            try:
                for i in xrange(10000):
                    print sql + ','.join(inserts[i * 1000: (i + 1) * 1000])
                    cursor.execute(sql + ','.join(inserts[i * 1000: (i + 1) * 1000]))
                    cursor.commit()
                    if (i + 1) * 1000 > len(inserts):
                        break
            except pyodbc.IntegrityError:
                print 'IntegrityError'
        else:
            print 'has no nan data'

    def delete(self, code, date):
        sql = "delete from {} where CONTRACTID = '{}' and TDATETIME = '{}'".format(self.get_table(date), code, date)
        cursor = self.get_cursor(date)
        cursor.execute(sql)
        cursor.commit()


def get_bar_date_time(period_int, date_time):
    dt_start_date_time = datetime.datetime(date_time.year,
                                           date_time.month,
                                           date_time.day,
                                           date_time.hour,
                                           (date_time.minute / period_int) * period_int)
    return dt_start_date_time + datetime.timedelta(minutes=period_int)


class Opr(object):
    def __init__(self):
        self.close = -1
        self.open = -1
        self.high = float('-inf')
        self.low = float('inf')
        self.oi = 0
        self.volume = 0
        self.amt = 0
        self.current_bar_dt = None
        self.period = ''
        self.ins = None
        self.bars = []
        self.db_opr = DBOper()

    def update(self, data):
        self.close = data[2]
        if self.high < data[4]:
            self.high = data[4]
        if self.low > data[5]:
            self.low = data[5]
        self.oi = data[6]
        self.volume += data[7]
        self.amt += data[8]
        print 'update', data[0], data[1]

    def write(self):
        if len(self.bars) == 0:
            last = [None, None, self.open, self.close, self.high, self.low, 0, 0, 0, 0, 0]
        else:
            last = self.bars[-1]
        l_close = last[3]
        open,close,high,low,chg,pct_chg,oi,volume,amt = \
            self.open, self.close, self.high, self.low, self.close - l_close, (self.close - l_close) / l_close, self.oi, self.volume, self.amt
        self.bars.append([self.current_bar_dt, self.ins, open,close,high,low,chg,pct_chg,oi,volume,amt])
        print 'write', self.current_bar_dt

    def init(self, data):
        self.current_bar_dt = get_bar_date_time(int(self.period), data[0])
        self.ins = data[1]
        self.close = data[2]
        self.open = data[3]
        self.high = data[4]
        self.low = data[5]
        self.oi = data[6]
        self.volume = data[7]
        self.amt = data[8]
        print 'init', data[0], data[1]

    def start(self, start, end, period):
        self.period = period
        instruments = get_all_instruments(start, end)
        print 'add instruments', len(instruments)

        for ins in instruments:
            data = get_data(ins, start, end)
            for line in data:
                if self.current_bar_dt is None:
                    self.init(line)
                else:
                    date_time = format_dt(line[0], ms=False)
                    if date_time <= self.current_bar_dt:
                        self.update(line)
                    else:
                        self.write()
                        self.init(line)
            self.write()
            if self.current_bar_dt is not None:
                self.db_opr.insert(period, self.bars)
            else:
                print 'ins', ins, 'insert', 0
            self.bars = []
            self.current_bar_dt = None

Opr().start(datetime.datetime(2016, 6, 1), datetime.datetime(2016, 6, 30, 23, 59, 59),  '05')
