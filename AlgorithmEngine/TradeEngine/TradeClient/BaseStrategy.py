import time

from Common.RedisClient import getAutoRedisDict
from TradeEngine.GlobleConf import RedisKey, AdjustConf
from TradeEngine.GlobleConf import SysWidget, StrategyWidget, Sys
from TradeEngine.MonitorClient import Monitor
from TradeEngine.OnBarDataStruct import OnBarData
from TradeEngine.TradeServer.OnRtnEventDiver import OnRtnEventDiver
from TradeEngine.GlobleConf import Sys


class BaseStrategy(object):
    def __init__(self, strategy_name, config, *args, **kwargs):
        self.__logger = Monitor.get_logger('%s:%s' % (strategy_name, config.name))
        self.__strategy_name = strategy_name
        self.__name = config.name
        self.__shares = StrategyWidget.get_shares_mgr(self.strategy_name)
        self.__config = config
        self.instruments = config.instruments
        self.param = config.param
        self.__sub_keys = None
        self.before_start()

    def debug(self, msg, *args):
        self.__logger.DEBUG(msg, *args)

    def info(self, msg, *args):
        self.__logger.INFO(msg, *args)

    def err(self, msg, *args):
        self.__logger.ERR(msg, *args)

    def warn(self, msg, *args):
        self.__logger.WARN(msg, *args)

    def before_start(self):
        pass

    @property
    def strategy_name(self):
        return self.__strategy_name

    @property
    def name(self):
        return self.__name

    @property
    def logger(self):
        return self.__logger

    @property
    def shares(self):
        self.__shares.update()
        return self.__shares.getDictShares()

    @property
    def auto_save_dict(self):
        return self.get_auto_save_dict()

    def adjust_to(self, instrument, volume, retry_times=AdjustConf.MaxTry):
        return SysWidget.get_remote_strategy_caller(self.strategy_name).adjust_to(self.name, instrument, volume,
                                                                                  retry_times)
    def adjustTo(self, instrument, volume, retry_times=AdjustConf.MaxTry):
        self.adjust_to(instrument, volume, retry_times)

    def get_shares_volume(self, instrument=None, direction=None):
        self.__shares.update()
        return self.__shares.get_shares(instrument, direction)

    def getSharesVolume(self, instrument=None, direction=None):
        return self.get_shares_volume(instrument, direction)

    def get_shares_price(self, instrument=None, direction=None):
        self.__shares.update()
        return self.__shares.get_price(instrument, direction)

    def getSharesPrice(self, instrument=None, direction=None):
        return self.get_shares_price(instrument, direction)

    def get_auto_save_dict(self, key=None):
        if not key:
            key = self.name
        return getAutoRedisDict(self.strategy_name, key)

    def getAutoSaveDict(self, key=None):
        return self.get_auto_save_dict(key)

    def set_states(self, key, value):
        SysWidget.get_redis_reader().setState(self.strategy_name, self.name, key, value)

    def setStates(self, key, value):
        self.set_states(key, value)

    def set_state_dict(self, states):
        SysWidget.get_redis_reader().setStates(self.strategy_name, self.name, states)

    def setStateDict(self, states):
        self.set_state_dict(states)

    def start(self):
        self.logger.INFO('START')
        self.__sub_keys = [RedisKey.Publish.Data(period, instrument) for instrument, period in self.__config.instruments_and_period]
        self.info('sub_keys:%s', str(self.__sub_keys))
        SysWidget.get_redis_reader().subscribe(self.__sub_keys, self._on_tick)
        SysWidget.get_remote_strategy_caller().start_strategy(self.name, self.instruments)
        return self

    def stop(self):
        self.logger.INFO('STOP')
        SysWidget.get_redis_reader().unsubscribe(self.__sub_keys, self._on_tick)

    def _on_tick(self, msg):
        ot_time = time.time()
        bar = OnBarData(OnRtnEventDiver.parse(msg['data']))
        if bar.get('MKStart') and bar.get('MINStart'):
            Sys.time_profile_init(self.__strategy_name, self.name, 'mk_min', float(bar['MKStart']))
            Sys.time_profile_end(self.__strategy_name, self.name, 'mk_min', float(bar['MINStart']))
            Sys.time_profile_init(self.__strategy_name, self.name, 'min_process', float(bar['MINStart']))
            Sys.time_profile_end(self.__strategy_name, self.name, 'min_process', float(bar['MINSend']))
            Sys.time_profile_init(self.__strategy_name, self.name, 'min_strategy', float(bar['MINSend']))
            Sys.time_profile_end(self.__strategy_name, self.name, 'min_strategy')
        self.on_bars(bar)
        Sys.time_profile_init(self.__strategy_name, self.name, 'on_tick', ot_time)
        Sys.time_profile(self.__strategy_name, self.name, 'bar_price', str(bar.BarClose))
        Sys.time_profile_end(self.__strategy_name, self.name, 'on_tick')

    def on_bars(self, data):
        self.onBars(data)

    def onBars(self, data):
        pass
