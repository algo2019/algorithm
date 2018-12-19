from Common.RedisClient import getAutoRedisDict
from TradeEngine.GlobleConf import SysWidget


class MarketData(object):
    Events = {}

    @classmethod
    def subscribe(cls, instrument, func):
        if cls.Events.get(instrument) is None:
            cls.Events[instrument] = []
        cls.Events[instrument].append(func)

    @classmethod
    def emit(cls, instrument, data):
        for func in cls.Events.get(instrument, []):
            func(data)


class BaseStrategy(object):
    positions = {}
    ticks = {}

    def __init__(self, strategy_name, config, *args, **kwargs):
        print 'test:', strategy_name, config.name
        self.__strategy_name = strategy_name
        self.__name = config.name
        self.__config = config
        self.instruments = config.instruments
        self.param = config.param
        self.before_start()

    def debug(self, msg, *args):
        print 'debug', msg, args

    def info(self, msg, *args):
        print 'info', msg, args

    def err(self, msg, *args):
        print 'err', msg, args

    def warn(self, msg, *args):
        print 'warn', msg, args

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
        class TempLogger(object):
            @classmethod
            def INFO(cls, *args, **kwargs):
                print 'info', args, kwargs

            @classmethod
            def DEBUG(cls, *args, **kwargs):
                print 'debug', args, kwargs

            @classmethod
            def ERR(cls, *args, **kwargs):
                print 'err', args, kwargs

            @classmethod
            def WARN(cls, *args, **kwargs):
                print 'warn', args, kwargs

        return TempLogger

    @property
    def shares(self):
        raise NotImplementedError

    @property
    def auto_save_dict(self):
        return self.get_auto_save_dict()

    def adjust_to(self, instrument, volume, retry_times=1):
        print 'adjust_to', self.name, instrument, 'target', volume
        old = self.positions.get(instrument, (0, 0))
        if volume * old[0] < 0:
            self.positions[instrument] = (volume, self.ticks[instrument])
        elif volume == 0:
            self.positions[instrument] = (0, 0)
        elif abs(volume) > abs(old[0]):
            cost = (abs(volume) - abs(old[0])) * self.ticks[instrument] + abs(old[0]) * old[1]
            self.positions[instrument] = (volume, cost/abs(volume))


    def adjustTo(self, instrument, volume, retry_times=1):
        self.adjust_to(instrument, volume, retry_times)

    def get_shares_volume(self, instrument=None, direction=None):
        v = self.positions.get(instrument, (0, 0))[0]
        if direction is None:
            return v
        if direction == '0':
            if v > 0:
                return v
            return 0
        if direction == '1':
            if v < 0:
                return v
            return 0

    def getSharesVolume(self, instrument=None, direction=None):
        return self.get_shares_volume(instrument, direction)

    def get_shares_price(self, instrument=None, direction=None):
        v = self.positions.get(instrument, (0, 0))[1]
        if direction is None:
            return v
        if direction == '0':
            if v > 0:
                return v
            return 0
        if direction == '1':
            if v < 0:
                return v
            return 0

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
        for instrument in self.instruments:
            MarketData.subscribe(instrument, self.__on_tick)
        return self

    def stop(self):
        raise NotImplementedError

    def __on_tick(self, msg):
        self.ticks[msg.InstrumentID] = msg.DayClose
        self.on_bars(msg)

    def on_bars(self, data):
        self.onBars(data)

    def onBars(self, data):
        pass
