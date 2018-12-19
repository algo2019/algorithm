from TradeEngine.GlobleConf import StrategyEvent
from TradeEngine.MonitorClient import Monitor
from TradeEngine.GlobleConf import SysEvents, Sys
from Common.RedisClient import AutoRedisDict
from TradeEngine import GlobleConf
import datetime
from tools import format_to_datetime as fdt
import threading
from TradeEngine.GlobleConf.RedisKey import DB


class Shares(object):
    LONG = GlobleConf.Shares.Long
    SHORT = GlobleConf.Shares.Short

    def __init__(self, strategy_name):
        self.__logger = Monitor.get_server_log('Shares:%s' % strategy_name)
        self.__strategy_name = strategy_name
        self.__lock = threading.Condition()
        self.__auto_save = AutoRedisDict.create(strategy_name, DB.Strategy.Sys())
        self.__trades = set()
        self.__load()
        self.__stoped = True
        self.start()
        self.__logger.INFO(msg='started')

    def update(self):
        Sys.time_profile_init(self.__strategy_name, 'Shares', 'update')
        self.__load()
        Sys.time_profile_end(self.__strategy_name, 'Shares', 'update')

    def start(self):
        if self.__stoped:
            self.__stoped = False
            StrategyEvent.get_order_state_change(self.__strategy_name).subscribe(self.update_shares)
            SysEvents.OnTickData.subscribe(self.check_next_day_and_update_yesterday_shares)

    def __save(self):
        Sys.time_profile_init(self.__strategy_name, 'Shares', 'save')
        self.__lock.acquire()
        self.__auto_save[DB.Strategy.Shares()] = (
            self.__date, self.__shares, self.__today_shares, self.__yesterday_shares, self.__price, self.__dict_shares)
        self.__lock.release()
        StrategyEvent.get_shares_change().emit(self.__strategy_name)
        Sys.time_profile_end(self.__strategy_name, 'Shares', 'save')

    def __load(self):
        self.__lock.acquire()
        if self.__auto_save[DB.Strategy.Shares()] is None:
            self.clear()
        self.__date, self.__shares, self.__today_shares, self.__yesterday_shares, self.__price, self.__dict_shares = \
            self.__auto_save.get_with_update(DB.Strategy.Shares())
        self.__lock.release()

    def clear(self):
        self.__lock.acquire()
        self.__auto_save[DB.Strategy.Shares()] = (
            datetime.datetime.now().date(),
            {self.LONG: {}, self.SHORT: {}},
            {self.LONG: {}, self.SHORT: {}},
            {self.LONG: {}, self.SHORT: {}},
            {self.LONG: {}, self.SHORT: {}},
            {self.LONG: {}, self.SHORT: {}}
        )
        self.__load()
        self.__lock.release()
        StrategyEvent.get_shares_change().emit(self.__strategy_name)

    def stop(self):
        if not self.__stoped:
            self.__stoped = True
            StrategyEvent.get_order_state_change(self.__strategy_name).unsubscribe(self.update_shares)
            SysEvents.OnTickData.unsubscribe(self.check_next_day_and_update_yesterday_shares)

    @staticmethod
    def __get_shares(shares__dict, instrument, direction):
        if instrument:
            if direction:
                return shares__dict[direction].get(str(instrument), 0)
            else:
                return {d: shares__dict[d].get(instrument, 0) for d in shares__dict}
        else:
            return shares__dict

    def get_date(self):
        return self.__date

    def get_today_shares(self, instrument=None, direction=None):
        return self.__get_shares(self.__today_shares, instrument, direction)

    def get_yesterday_shares(self, instrument=None, direction=None):
        return self.__get_shares(self.__yesterday_shares, instrument, direction)

    def get_shares(self, instrument=None, direction=None):
        return self.__get_shares(self.__shares, instrument, direction)

    def get_price(self, instrument=None, direction=None):
        return self.__get_shares(self.__price, instrument, direction)

    def get_instruments(self, direction):
        return [instrument for instrument in self.__shares[direction]]

    def get_dict_shares(self):
        return self.__dict_shares

    def check_next_day_and_update_yesterday_shares(self, on_bar_data):
        if fdt(on_bar_data.TradingDay, time=False) > self.__date:
            self.__date = fdt(on_bar_data.TradingDay, time=False)
            for offset in self.__today_shares:
                for instrument in self.__today_shares[offset]:
                    self.__yesterday_shares[offset][instrument] = self.__yesterday_shares[offset].get(instrument, 0) + \
                                                                  self.__today_shares[offset][instrument]
                    self.__today_shares[offset][instrument] = 0
            self.__save()

    def __update_today_and_yesterday(self, trade):
        los = trade.long_or_short
        code = trade.instrument
        if not self.__today_shares[los].get(code):
            self.__today_shares[los][code] = 0
        if trade.is_open():
            self.__today_shares[los][code] += trade.volume
        else:
            if self.__today_shares[los][code] >= trade.volume:
                self.__today_shares[los][code] -= trade.volume
            else:
                yesterday_close = trade.volume - self.__today_shares[los][code]
                self.__yesterday_shares[los][code] -= yesterday_close
                del self.__today_shares[los][code]
                if self.__yesterday_shares[los][code] == 0:
                    del self.__yesterday_shares[los][code]

    @staticmethod
    def __trade_key(trade):
        return '{}.{}'.format(trade.order_ref, trade.trade_id)

    def __update_shares_and_price(self, trade):
        if trade.volume == 0:
            return
        self.__trades.add(self.__trade_key(trade))
        los = trade.long_or_short
        code = trade.instrument
        if not self.__shares[los].get(code):
            self.__shares[los][code] = 0
            self.__price[los][code] = 0
        if trade.is_open():
            cost = self.__shares[los][code] * self.__price[los][code] + trade.volume * trade.price
            volume = self.__shares[los][code] + trade.volume
            self.__price[los][code] = cost / volume
            self.__shares[los][code] += trade.volume
        else:
            if self.__shares[los][code] - trade.volume < 0:
                raise Exception(
                    'Shares:%s hold:%d covered:%d' % (trade.instrument, self.__shares[los][code], trade.volume))
            self.__shares[los][code] -= trade.volume
            if self.__shares[los][code] == 0:
                del self.__shares[los][code]
                del self.__dict_shares[los][code]
        if self.__shares[los].get(code):
            self.__dict_shares[los][code] = [self.__shares[los][code], self.__price[los][code]]

    def update_shares(self, order):
        trade = order.last_trade
        if trade is None or self.__trade_key(trade) in self.__trades:
            return
        Sys.time_profile_init(self.__strategy_name, 'Shares', 'update_shares')
        old = self.get_shares(trade.instrument, trade.long_or_short)
        self.__update_today_and_yesterday(trade)
        self.__update_shares_and_price(trade)
        self.__save()
        new = self.get_shares(trade.instrument, trade.long_or_short)
        self.__logger.INFO(self.__strategy_name, 'update:%s offset:%s from:%d to:%d', trade.instrument,
                           trade.long_or_short, old, new)
        Sys.time_profile_end(self.__strategy_name, 'Shares', 'update_shares')
