import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '..', '..')))
sys.path.append('/data/xingwang.zhang/running/AlgorithmEngine')

import abc
import time
import re
from tools import format_to_datetime
from External.GTADBOperator import GTADBOperator
from Common.PubSubAdapter.RedisPubSub import RedisPubSub
from Common.CommonLogServer.RedisLogService.LogCommands import PublishLogCommand
import traceback


dtf = format_to_datetime


def get_dict_data(data):
    if type(data) is dict:
        data = data['data']
    return {item[0]: item[1] for item in (i.split('#') for i in data.split('|'))}


class MarketDataWriter(object):
    table_caller_class = {}

    def __init__(self, period):
        self.__period = period
        self.__market_caller = {}
        for tw_name in self.table_caller_class:
            markets, tw_class = self.table_caller_class[tw_name]
            tw_instance = tw_class(self.__period)
            for mk in markets:
                self.__market_caller[mk] = tw_instance

    @classmethod
    def register(cls, tw_name, table_writer_class, markets):
        cls.table_caller_class[tw_name] = (markets, table_writer_class)

    def update(self, data):
        try:
            if data['type'] == 'pmessage':
                dict_data = get_dict_data(data)
                caller = self.__market_caller.get(dict_data['ExchangeID'])
                if caller is not None:
                    caller.update(dict_data)
        except:
            PublishLogCommand('Main', 'Opr', 'WriteMarketDataToGTA', 'ERR', 'update', traceback.format_exc(), tuple()).execute()


class BaseTableWriter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, period):
        self._operator = GTADBOperator()
        self._operator.start()
        self._period = period
        self._dataBase = None
        self._table = None

    @abc.abstractmethod
    def _get_db_and_table(self, ym):
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
        db_name, table_name = self._get_db_and_table(ym)
        if db_name != self._dataBase:
            self._dataBase = db_name
            self._table = table_name

    @abc.abstractmethod
    def _write(self, data):
        raise NotImplementedError


class FutTableWriter(BaseTableWriter):
    def _get_db_and_table(self, ym):
        return self._operator.getFutMinDBName(ym), self._operator.getFutMinTableName(self._period, ym)

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
    def _get_db_and_table(self, ym):
        return self._operator.getFFutMinDBName(ym), self._operator.getFFutMinTableName(self._period, ym)

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
    min_list = ['01', '05', '10', '15', '30']
    per_fix = 'CTP.minData'

    redis_host = '10.4.27.181'
    redis_port = 6379
    print 'min_list', min_list
    print 'redis_host', redis_host
    MarketDataWriter.register('fut', FutTableWriter, {'DLFX', 'ZZFX', 'SHFX'})
    MarketDataWriter.register('ffut', FFutTableWriter, {'CFFEX'})
    print 'register market data ready'
    ps = RedisPubSub(redis_host, redis_port)
    for min_str in min_list:
        key = '%s.%s.*' % (per_fix, min_str)
        ps.subscribe(key, MarketDataWriter(min_str).update)
        print 'subscribe {} ready'.format(key)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        os.system('python {} start'.format(__file__))
        PublishLogCommand('Main', 'Opr', 'WriteMarketDataToGTA', 'ERR', 'running', 'program exit: {}'.format(os.path.abspath(__file__)), tuple()).execute()
    elif len(sys.argv) == 2 and sys.argv[1] == 'start':
        main()
        while 1:
            time.sleep(10)
    else:
        raise Exception('argv: {} undefined'.format(str(sys.argv)))
