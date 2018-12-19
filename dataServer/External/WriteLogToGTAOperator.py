import abc
import time

import re

from External.GTADBOperator import GTADBOperator
from tools import format_to_datetime
import sys
dtf = format_to_datetime


class MarketDataWriter(object):
    table_caller_class = {}

    def __init__(self):
        self.__market_caller = {}
        for tw_name in self.table_caller_class:
            markets, tw_class = self.table_caller_class[tw_name]
            tw_instance = tw_class()
            for mk in markets:
                self.__market_caller[mk] = tw_instance

    @classmethod
    def register(cls, tw_name, table_writer_class, markets):
        cls.table_caller_class[tw_name] = (markets, table_writer_class)

    def update(self):
        for line in sys.stdin:
            dict_data = eval(line.split("'turnover'")[1])
            dict_data['turnover'] = dict_data['amt']
            caller = self.__market_caller.get(dict_data['ExchangeID'])
            if caller is not None:
                caller.update(dict_data)


class BaseTableWriter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._operator = GTADBOperator()
        self._operator.start()
        self._dataBase = None
        self._table = None

    @abc.abstractmethod
    def _get_db_and_table(self, ym, period):
        raise NotImplementedError

    def update(self, dict_data):
        self._update_db_table(dict_data)
        try:
            self._write(dict_data)
        except Exception, e:
            print e, dict_data

    def _update_db_table(self, data):
        trading_date = dtf(data['dateTime'])
        ym = '%4.4d%2.2d' % (trading_date.year, trading_date.month)
        db_name, table_name = self._get_db_and_table(ym, data['period'])
        if db_name != self._dataBase:
            self._dataBase = db_name
            self._table = table_name

    @abc.abstractmethod
    def _write(self, data):
        raise NotImplementedError


class FutTableWriter(BaseTableWriter):
    def _get_db_and_table(self, ym, period):
        return self._operator.getFutMinDBName(ym), self._operator.getFutMinTableName(period, ym)

    def _write(self, data):
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
        MARKET = data['ExchangeID']
        UNIX = int(time.time() * 1000)
        self._operator.insertValue(
            self._dataBase, self._table,
            (CONTRACTID, TDATETIME, OPENPX, HIGHPX, LOWPX, LASTPX, MINQTY, TURNOVER, OPENINTS, CHGMIN, CHGPCTMIN,
             VARIETIES, MFLXID, MARKET, UNIX)
        )


class FFutTableWriter(BaseTableWriter):
    def _get_db_and_table(self, ym, period):
        return self._operator.getFFutMinDBName(ym), self._operator.getFFutMinTableName(self.period, ym)

    def _write(self, data):
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
        MARKET = data['ExchangeID']
        UNIX = 0
        self._operator.insertValue(
            self._dataBase, self._table,
            (IFCD, TDATE, TTIME, OPNPRC, CLSPRC, HIPRC, LOPRC, CHG, CHGPCT, OPNINTRST, MINTQ, MINTM,
             IFLXID, IFLXNAME, UNIX, MARKET)
        )


def main():
    MarketDataWriter.register('fut', FutTableWriter, {'DLFX', 'ZZFX', 'SHFX'})
    MarketDataWriter.register('ffut', FFutTableWriter, {'CFFEX'})
    MarketDataWriter().update()


if __name__ == '__main__':
    main()
