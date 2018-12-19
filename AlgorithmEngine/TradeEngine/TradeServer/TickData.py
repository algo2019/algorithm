import cPickle as pickle

import redis

from Common.Command import Command
from TradeEngine.GlobleConf import OnBarData
from TradeEngine.GlobleConf import SysWidget, SysEvents
from TradeEngine.GlobleConf.RedisKey import Publish
from TradeEngine.MonitorClient import Monitor
from TradeEngine.TradeServer.OnRtnEventDiver import OnRtnEventDiver
from Common.Dao.TickDataDao import TickDataDao


class TickDataError(Exception):
    pass


class TickData(object):
    def __init__(self):
        self.__ticks = {}
        self.__saved_instruments = set()
        self.__redis = None
        self.__logger = Monitor.get_logger('TickData')
        self.__tick_dao = TickDataDao()
        self.__redis = SysWidget.get_redis_reader()

    def __getitem__(self, item):
        return self.get(item)

    def add_instrument(self, instrument):
        self.get(instrument)

    def add_instruments(self, instruments):
        for instrument in instruments:
            self.add_instrument(instrument)

    @property
    def instrument_set(self):
        return self.__saved_instruments

    def __update_tick_data(self, message):
        SysWidget.get_log_engine().add_command(Command(target=self.__main_process, args=(message, )))

    def __main_process(self, message):
        tick_data = OnBarData(OnRtnEventDiver.parse(message['data']))
        self.__ticks[tick_data.InstrumentID] = tick_data
        SysEvents.OnTickData.emit(tick_data)

    def get(self, instrument):
        if instrument not in self.__saved_instruments:
            sub_key = Publish.Data('00', instrument)
            self.__redis.subscribe(sub_key, self.__update_tick_data)
            self.__saved_instruments.add(instrument)
            bar = self.__tick_dao.get(instrument)
            if bar is None:
                raise TickDataError('instrument:%s can not get tick data for hash db' % instrument)
            self.__ticks[instrument] = bar
        return self.__ticks[instrument]
