import datetime

import re

import tools
import pyodbc
from pprint import pprint
from dataServer import dataServer
from dataBaseAPI import dataBaseClient

w = dataServer('10.2.53.43')
d = dataBaseClient.w
w.start()

period = 1


def get_data(ins, start, end):
    d.start()
    conf = {
        'dataName': 'data',
        'code': ins,
        'fields': 'close,open,high,low,volume',
        'start': start,
        'end': end,
        'period': '{}m'.format(period),
    }
    res = d.wmm(conf)
    d.stop()
    return res


def get_all_instruments(dt):
    print 'get all instrument of', dt
    d.start()
    conf = {
        'dataName': 'sql',
        'sql': "select SYMBOL from FFUT_QUOTATION where TRADINGDATE='{}' group by SYMBOL;".format(d.tdaysoffset(0, dt.date()).Data[0][0])
    }
    rt = d.wmm(conf)
    d.stop()
    return [str(i[0]) for i in rt]


def get_all_instruments_min(start, end):
    print 'get all instruments of min', start, end
    d.start()
    conf = {
        'dataBaseName': 'GTA_FFL2_TRDMIN_{}{:0>2}'.format(start.year, start.month),
        'dataName': 'sql',
        'sql': "select IFCD from FFL2_TRDMIN{:0>2}_{s_y}{s_m:0>2} where TDATE >='{s_y}{s_m:0>2}{s_d:0>2}' and TDATE<'{e_y}{e_m:0>2}{e_d:0>2}' group by IFCD".format(
            period, s_y=start.year, s_m=start.month, s_d=start.day, e_y=end.year, e_m=end.month, e_d=end.day)
    }
    rt = d.wmm(conf)
    d.stop()
    return [str(i[0]) for i in rt]


def next_day(dt):
    return dt + datetime.timedelta(days=1)


class DBOpr(object):
    def __init__(self):
        self.db_dt = None
        self.db_per_fix = 'GTA_FFL2_TRDMIN_{}'
        self.conn = None
        self.cursor = None

    def connect(self, date_time):
        self.conn = pyodbc.connect(
            "DRIVER={{SQL Server}};SERVER=10.4.27.179;port=1433;UID=gta_updata;PWD=rI2016;DATABASE={};TDS_Version=8.0" \
                .format(self.db_per_fix.format(date_time.strftime('%Y%m'))))
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

    @staticmethod
    def get_table(date_time):
        return "FFL2_TRDMIN{:0>2}_{}".format(period, date_time.strftime('%Y%m'))

    def insert(self, wsi_res):
        dt = wsi_res.Times[0]
        cursor = self.get_cursor(dt)
        ln = 'IFCD, TDATE, TTIME, OPNPRC, CLSPRC, HIPRC, LOPRC, CHG, CHGPCT, OPNINTRST, MINTQ, MINTM, IFLXID, IFLXNAME, UNIX, MARKET'
        sql = 'insert into {}({})values'.format(self.get_table(dt), ln)
        ifcd = wsi_res.Codes[0].split('.')[0]
        values = []
        for i in xrange(len(wsi_res.Times)):
            ds = [x[i] for x in wsi_res.Data]
            s = sum(ds)
            if s != s:
                continue
            dt = wsi_res.Times[i]
            tdate = dt.strftime('%Y%m%d')
            ttime = dt.strftime('%H%M')
            opn, cls, hi, lw, chg, chgpct, io, mq, mt = ds
            values.append(
                "('{}', '{}', '{}', '{:.2f}', '{:.2f}', '{:.2f}', '{:.2f}', '{:.2f}', '{:.4f}', '{}', '{:.0f}', '{:.2f}', '-', '-', '0', '-')".format(
                    ifcd, tdate, ttime, opn, cls, hi, lw, chg, chgpct, io, mq, mt))
        if len(values) != 0:
            try:
                for i in xrange(10000):
                    print sql + ','.join(values[i * 1000: (i + 1) * 1000])
                    cursor.execute(sql + ','.join(values[i * 1000: (i + 1) * 1000]))
                    cursor.commit()
                    if (i + 1) * 1000 > len(values):
                        break
            except pyodbc.IntegrityError:
                print ifcd, 'IntegrityError'
        else:
            print 'has no nan data'


def get_wsi_date(ins, start, end):
    print 'wsi', ins, start, end
    return w.wsi(ins, 'open,close,high,low,chg,pct_chg,oi,volume,amt', start, end, 'BarSize={}'.format(period))


DBOpr = DBOpr()


def update_all(start, end, symbol=None, instrument=None):
    print 'period is ', period
    instruments = get_instrument_day_min()
    print 'special symbol is', symbol
    print 'instrument need to update is ', len(instruments)
    if len(instruments) < 50:
        pprint(instruments)

    instruments.sort()
    f = False
    if instrument is not None:
        f = True

    for ins in instruments:
        if ins == instrument:
            f = False
        if f:
            continue
        if symbol is not None and symbol not in ins:
            continue

        print 'start to update', ins
        if len(get_data(ins, start, end)) > 0:
            print 'has data in min'
            continue
        if ins is None:
            print 'ins is None'
            continue
        print 'start update', start, end
        res = get_wsi_date('{}.{}'.format(ins, tools.get_exchange_id(ins)), start, end)
        if type(res.Data[0][0]) == unicode:
            print ins, res.Data[0][0]
            continue
        DBOpr.insert(res)


def get_instrument_day_min():
    return list((set(get_all_instruments(start)) | set(get_all_instruments(end))) - set(get_all_instruments_min(start, end)))


def next_month(dt):
    if dt.month == 12:
        return dt.replace(month=1, year=dt.year+1)
    else:
        return dt.replace(month=dt.month + 1)

start = datetime.datetime(2015, 8, 1)
end = datetime.datetime(2015, 9, 1)
for i in [1, 5, 10, 15]:
    period = i
    update_all(start, end)
start = next_month(start)
