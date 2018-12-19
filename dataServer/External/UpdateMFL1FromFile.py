import os
import re
import time
import pyodbc
import sys

import datetime

max_len = 999


def get_dict_data(data):
    if type(data) is dict:
        data = data['data']
    return {item[0]: item[1] for item in (i.split('#') for i in data.split('|'))}


def format_to_datetime(dt, time=True, date=True, ms=True):
    ds = re.match(r'\s*(?:(\d{4})[\:\-\/]?(\d{2})[\:\-\/]?(\d{2}))?\s?(?:(\d{2}):?(\d{2}):?(\d{2})\.?(\d+)?)?\s*',
                  str(dt))
    if ds is not None:
        if not time:
            return datetime.date(*map(int, ds.groups(default=0)[:3]))
        if not date:
            if not ms:
                return datetime.time(*map(int, ds.groups(default=0)[3:6]))
            return datetime.time(*map(int, ds.groups(default=0)[3:]))
        if not ms:
            return datetime.datetime(*map(int, ds.groups(default=0)[:6]))
        return datetime.datetime(*map(int, ds.groups(default=0)))
    else:
        raise Exception('format_to_datetime: can not format {} to datetime'.format(dt))


class DBOpr(object):
    def __init__(self):
        self.db_dt = None
        self.conn = None
        self.cursor = None
        self.UpFlag = True

    def connect(self, db):
        self.conn = pyodbc.connect(
            "DRIVER={{SQL Server}};SERVER=10.4.27.179;port=1433;UID=gta_updata;PWD=rI2016;DATABASE={};TDS_Version=8.0" \
                .format(db))
        self.cursor = self.conn.cursor()

    def get_cursor(self, ym):
        if self.db_dt is None:
            self.db_dt = ym
            self.connect(ym)
            return self.cursor
        elif ym == self.db_dt:
            return self.cursor
        else:
            self.cursor.close()
            self.conn.close()
            self.db_dt = ym
            self.connect(ym)
            return self.cursor

    @staticmethod
    def get_mf_table(period, date_time):
        return "MFL1_TRDMIN{:0>2}_{}".format(period, date_time.strftime('%Y%m'))

    @staticmethod
    def get_ff_table(period, date_time):
        return "FFL2_TRDMIN{:0>2}_{}".format(period, date_time.strftime('%Y%m'))

    def write_to_db(self, ym, table_name, inserts):
        if table_name.startswith('FFL2'):
            return

        if table_name.startswith('MFL1_TRDMIN'):
            ln = 'CONTRACTID, TDATETIME, OPENPX, HIGHPX, LOWPX, LASTPX, MINQTY, TURNOVER, OPENINTS, CHGMIN, CHGPCTMIN, VARIETIES, MFLXID, MARKET, UNIX'
            db = 'GTA_MFL1_TRDMIN_{}'.format(ym)
        else:
            ln = 'IFCD, TDATE, TTIME, OPNPRC, HIPRC, LOPRC, CLSPRC, MINTQ, MINTM, OPNINTRST, CHG, CHGPCT, IFLXID, IFLXNAME, MARKET, UNIX'
            db = 'GTA_FFL2_TRDMIN_{}'.format(ym)

        if not self.UpFlag:
            return
        cursor = self.get_cursor(db)

        sql = 'insert into {}({}) values '.format(table_name, ln)
        print sql + ','.join(filter(lambda x: x, inserts))
        print ym, table_name, 'insert . . .'
        cursor.execute(sql + ','.join(filter(lambda x: x, inserts)))
        cursor.commit()

    def update_mfl1(self, data, inserts):
        MARKET = data['ExchangeID']
        if MARKET == '':
            inserts.append(None)
            return
        CONTRACTID = data['InstrumentID'].upper()
        TDATETIME = data['dateTime']
        OPENPX = float(data['open'])
        HIGHPX = float(data['high'])
        LOWPX = float(data['low'])
        LASTPX = float(data['close'])
        MINQTY = int(data['volume'])
        TURNOVER = float(data['turnover'])
        OPENINTS = float(data['OpenInterest'])
        CHGMIN = LASTPX - OPENPX
        CHGPCTMIN = '%4.4f' % (CHGMIN / OPENPX)
        VARIETIES = '--'
        MFLXID = '--'
        UNIX = int(time.time() * 1000)
        inserts.append(
            "('{}', '{}', '{:.2f}', '{:.2f}', '{:.2f}', '{:.2f}', '{}', '{:.2f}', '{:.2f}', '{:.2f}', '{}', "
            "'{}', '{}', '{}', '{}')".format(
                CONTRACTID, TDATETIME, OPENPX, HIGHPX, LOWPX, LASTPX, MINQTY, TURNOVER, OPENINTS, CHGMIN, CHGPCTMIN,
                VARIETIES, MFLXID, MARKET, UNIX))

    def update_ffl2(self, data, inserts):
        MARKET = data['ExchangeID']
        if MARKET == '':
            inserts.append(None)
            return

        IFCD = data['InstrumentID'].upper()
        ds = re.match(r'(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):\d{2}(.\d+)?', data['dateTime'])
        TDATE = ds.group(1) + ds.group(2) + ds.group(3)
        TTIME = ds.group(4) + ds.group(5)
        OPNPRC = float(data['open'])
        HIPRC = float(data['high'])
        LOPRC = float(data['low'])
        CLSPRC = float(data['close'])
        MINTQ = int(data['volume'])
        MINTM = float(data['turnover'])
        OPNINTRST = float(data['OpenInterest'])
        CHG = CLSPRC - OPNPRC
        CHGPCT = '%4.4f' % (CHG / OPNPRC)
        IFLXID = '-'
        IFLXNAME = '-'
        UNIX = 0

        inserts.append(
            "('{}', '{}', '{}', '{:.2f}', '{:.2f}', '{:.2f}', '{:.2f}', '{}', '{:.2f}', '{:.2f}', '{:.2f}', '{}', '{}',"
            " '{}', '{}', '{}')".format(
                IFCD, TDATE, TTIME, OPNPRC, HIPRC, LOPRC, CLSPRC, MINTQ, MINTM, OPNINTRST, CHG, CHGPCT, IFLXID,
                IFLXNAME, MARKET, UNIX))

    def insert(self, datas):
        inserts = {}
        last = {}
        for line in datas:
            data = get_dict_data(line)

            if data['dateTime'] < '2017-04-28 13:00:00':
                continue

            dt = format_to_datetime(data['dateTime'])
            ym = dt.strftime('%Y%m')
            if data['ExchangeID'] == 'CFFEX':
                tale_name = self.get_ff_table(int(data['period']), dt)
            elif data['ExchangeID'] in {'SHFX', 'DLFX', 'ZZFX'}:
                tale_name = self.get_mf_table(int(data['period']), dt)
            else:
                continue
            if inserts.get(ym) is None:
                inserts[ym] = {}
            if inserts[ym].get(tale_name) is None:
                inserts[ym][tale_name] = []

            if last.get(data['InstrumentID']) is None:
                last[data['InstrumentID']] = {}
            if last[data['InstrumentID']].get(data['period']) is None:
                last[data['InstrumentID']][data['period']] = data['dateTime']
            elif last[data['InstrumentID']][data['period']] >= data['dateTime']:
                sys.stderr.write('{} {} last: {} now {}\n'.format(data['InstrumentID'], data['period'],
                                                                  last[data['InstrumentID']][data['period']],
                                                                  data['dateTime']))
                continue
            else:
                last[data['InstrumentID']][data['period']] = data['dateTime']

            if data['ExchangeID'] == 'CFFEX':
                self.update_ffl2(data, inserts[ym][tale_name])
            else:
                self.update_mfl1(data, inserts[ym][tale_name])

            if len(inserts[ym][tale_name]) == max_len:
                self.write_to_db(ym, tale_name, inserts[ym][tale_name])
                del inserts[ym][tale_name]

        for ym in inserts:
            for tale_name in inserts[ym]:
                self.write_to_db(ym, tale_name, inserts[ym][tale_name])


def update_all(file_name):
    DBOpr().insert(open(file_name, 'r').xreadlines())


def get_file_name(dt):
    return 'data/MinData.{}.{}'.format(dt.date(), dt.hour)


def update_times(times):
    for start, end in times:
        cur = start
        if cur < end:
            if os.path.exists(get_file_name(cur)):
                update_all(get_file_name(cur))
            cur += datetime.timedelta(hours=1)

update_all('/Users/renren1/PycharmProjects/AlgorithmEngine/MarketDataServer/head.data')