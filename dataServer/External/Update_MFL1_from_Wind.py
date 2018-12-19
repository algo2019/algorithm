import datetime

import re

import tools
import pyodbc
from pprint import pprint
from dataServer import dataServer
from dataBaseAPI.dataBaseClient import Client
w = dataServer('10.2.53.13')
d = Client()
d.start()
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
        'sql': "select SYMBOL from FUT_QUOTATIONHISTORY where TRADINGDATE='{}' group by SYMBOL;".format(d.tdaysoffset(0, dt.date()).Data[0][0])
    }
    rt = d.wmm(conf)
    d.stop()
    return [get_ins4(str(i[0])) for i in rt]


def get_all_instruments_min(start, end):
    print 'get all instruments of min', start, end
    d.start()
    conf = {
        'dataBaseName': 'GTA_MFL1_TRDMIN_{}{:0>2}'.format(start.year, start.month),
        'dataName': 'sql',
        'sql': "select CONTRACTID from MFL1_TRDMIN{:0>2}_{}{:0>2} where TDATETIME >='{}' and TDATETIME<'{}' group by CONTRACTID".format(period, start.year, start.month, start, end)
    }
    rt = d.wmm(conf)
    d.stop()
    return [get_ins4(str(i[0])) for i in rt]


def next_month(dt):
    targetmonth = 1 + dt.month
    try:
        dt = dt.replace(year=dt.year + int(targetmonth / 12), month=(targetmonth % 12))
    except:
        dt = dt.replace(year=dt.year + int((targetmonth + 1) / 12), month=((targetmonth + 1) % 12), day=1)
        dt += datetime.timedelta(days=-1)
    return dt


def next_day(dt):
    return dt + datetime.timedelta(days=1)


class DBOpr(object):
    def __init__(self):
        self.db_dt = None
        self.db_per_fix = 'GTA_MFL1_TRDMIN_{}'
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
        return "MFL1_TRDMIN{:0>2}_{}".format(period, date_time.strftime('%Y%m'))

    def insert(self, wsi_res):
        dt = wsi_res.Times[0]
        cursor = self.get_cursor(dt)
        ln = 'CONTRACTID, TDATETIME, OPENPX, HIGHPX, LOWPX, LASTPX, MINQTY, TURNOVER, OPENINTS, CHGMIN, CHGPCTMIN, VARIETIES, MFLXID, MARKET, UNIX'

        sql = 'insert into {}({})values'.format(self.get_table(dt), ln)
        inserts = []
        instrument = wsi_res.Codes[0].split('.')[0]
        print 'insert', instrument, wsi_res.Times[0], wsi_res.Times[-1]
        for i in xrange(len(wsi_res.Times)):
            ds = [x[i] for x in wsi_res.Data]
            if ds[-1] != ds[-1]:
                ds[-1] = -1
            s = sum(ds)
            if s != s:
                continue
            dt = wsi_res.Times[i]
            opn, cls, hi, lw, chg, chgpct, oi, mq, mt = ds
            inserts.append(
                "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{:.4f}', '-', '-', '-', '0')".format(
                    instrument, str(dt)[:19], opn, hi, lw, cls, mq, mt, oi, chg, chgpct))
        if len(inserts) != 0:
            try:
                for i in xrange(100):
                    print sql + ','.join(inserts[i * 1000: (i + 1) * 1000])
                    cursor.execute(sql + ','.join(inserts[i * 1000: (i + 1) * 1000]))
                    cursor.commit()
                    if (i + 1) * 1000 > len(inserts):
                        break
            except pyodbc.IntegrityError:
                print instrument, 'IntegrityError'
        else:
            print 'has no nan data'

    def delete(self, code, date):
        sql = "delete from {} where CONTRACTID = '{}' and TDATETIME = '{}'".format(self.get_table(date), code, date)
        cursor = self.get_cursor(date)
        cursor.execute(sql)
        cursor.commit()


def get_ins3(ins):
    s = re.match(r'(\D{1,2})(?:\d)?(\d{3})', ins)
    if s is None:
        return None
    return s.group(1) + s.group(2)


def get_ins4(ins):
    s = re.match(r'(\D{1,2})(?:\d)?(\d{3})', ins)
    if s is None:
        return None
    return s.group(1) + '1' + s.group(2)


def get_wsi_date(ins, start, end):
    print 'wsi', ins, start, end
    return w.wsi(ins, 'open,close,high,low,chg,pct_chg,oi,volume,amt', start, end, 'BarSize={}'.format(period))


DBOpr = DBOpr()


def update_all(start, end):
    print 'period is ', period
    instruments = get_instruments_day_min()
    print 'instrument need to update is ', len(instruments)
    if len(instruments) < 50:
        pprint(instruments)
    instruments.sort()
    for ins in instruments:
        print 'start to update', ins
        if len(get_data(ins, start, end)) > 0:
            print 'has data in min'
            continue
        if ins is None:
            print 'ins is None'
            continue
        if tools.get_exchange_id(ins) == 'CZC':
            ins = get_ins3(ins)
        print 'start update', start, end
        res = get_wsi_date('{}.{}'.format(ins, tools.get_exchange_id(ins)), start, end)
        if type(res.Data[0][0]) == unicode:
            print ins, res.Data[0][0]
            continue
        DBOpr.insert(res)


def get_instruments_day_min():
    # return get_all_instruments(start)
    return list((set(get_all_instruments(start)) | set(get_all_instruments(end))))
    # return list((set(get_all_instruments(start)) | set(get_all_instruments(end))) - set(get_all_instruments_min(start, end)))
#
# start = datetime.datetime(2016, 3, 1)
# end = datetime.datetime(2016, 4, 1)
#
# update_all(start, end)
