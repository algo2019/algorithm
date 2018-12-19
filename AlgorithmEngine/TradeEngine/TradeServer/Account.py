import threading, time
from TradeEngine.GlobleConf import StrategyEvent
from TradeEngine.TradeServer.Shares import Shares
from TradeEngine.GlobleConf import SysWidget, StrategyWidget, AccountConf, Sys
from TradeEngine.GlobleConf.RedisKey import DB
from Common.RedisClient import AutoRedisDict
from TradeEngine.MonitorClient import Monitor
from tradeutil import get_trade_unit


class Account(object):
    def __init__(self, strategy_name):
        self.__logger = Monitor.get_server_log('Account:%s' % strategy_name)
        self.__strategy_name = strategy_name
        self.__auto_save = AutoRedisDict.create(strategy_name, DB.Strategy.Sys())
        self.__ticks = SysWidget.get_tick_data()
        self.__lock = threading.Condition()
        self.__load()
        self.__shares = StrategyWidget.get_shares_mgr(strategy_name)
        self.__stoped = True
        self.__trades = set()
        self.__temp = {}
        self.start()
        self.__logger.INFO(self.__strategy_name, 'started')

    def start(self):
        if self.__stoped:
            self.__stoped = False
            StrategyEvent.get_order_state_change(self.__strategy_name).subscribe(self.__on_order_state_change)

    def stop(self):
        if not self.__stoped:
            self.__stoped = True
            StrategyEvent.get_on_rtn_trade(self.__strategy_name).unsubscribe(self.__on_order_state_change)

    def __load(self):
        if not self.__auto_save[DB.Strategy.Account()]:
            self.clear()
            return

        self.__lock.acquire()
        self.__account = self.__auto_save[DB.Strategy.Account()]
        default = self.default_conf
        for key in default:
            if self.__account.get(key) is None:
                self.__account[key] = default[key]

        self.__lock.release()

    def clear(self):
        self.__lock.acquire()
        self.__account = self.default_conf
        self.__save()
        self.__lock.release()

    @property
    def default_conf(self):
        cash = AccountConf.get(self.__strategy_name)
        if not cash:
            cash = AccountConf['default']
        return {
            'Available': cash,
            'Start': cash,
            'CloseProfit': 0.0,
            'Commission': 0.0,
            'MaxInterests': cash,
            'MaxDrawdownCash': 0.0,
        }

    def __save(self):
        self.__lock.acquire()
        self.__auto_save[DB.Strategy.Account()] = self.__account
        self.__lock.release()

    def __update_close_profit(self, trade):
        if trade.is_sell():
            close_profit = trade.price - self.__shares.get_price(trade.instrument, trade.long_or_short)
        else:
            close_profit = self.__shares.get_price(trade.instrument, trade.long_or_short) - trade.price
        close_profit *= get_trade_unit(trade.instrument) * trade.volume
        self.__account['Available'] += close_profit
        self.__account['CloseProfit'] += close_profit

    @staticmethod
    def __trade_key(trade):
        return '{}.{}'.format(trade.order_ref, trade.trade_id)

    def __on_order_state_change(self, order):
        Sys.time_profile_init(self.__strategy_name, 'Account', 'on_order_state_change')
        trade = order.last_trade
        if trade is None or self.__trade_key(trade) in self.__trades:
            return
        self.__lock.acquire()
        close_profit = self.__account['CloseProfit']
        commission = self.__account['Commission']
        self.__logger.INFO(self.__strategy_name, 'update:%s', trade.instrument)
        cur_commission = self._commission(trade.instrument, trade.price, trade.volume)
        if not trade.is_open():
            self.__update_close_profit(trade)
        self.__account['Available'] -= cur_commission
        self.__account['Commission'] += cur_commission
        self.__logger.INFO(self.__strategy_name, 'update:%s close_profit:%2.2f -> %2.2f commission:%2.2f -> %2.2f',
                           trade.instrument, close_profit, self.__account['CloseProfit'], commission,
                           self.__account['Commission'])
        self.__lock.release()
        self.__save()
        Sys.time_profile_end(self.__strategy_name, 'Account', 'on_order_state_change')

    def __shares_margin(self):
        shares = self.__shares.get_shares()
        margin = 0
        for los in shares:
            for instrument in shares[los]:
                margin += self._margin(instrument, self.__ticks.get(instrument).DayClose, shares[los][instrument])
        return margin

    def __active_order_margin(self, exclude_ref=None):
        hander = lambda order_list: sum(
            map(lambda order: self._margin(order.instrument, order.price, order.volume - order.filled_volume),
                filter(lambda order: order.order_ref != exclude_ref, order_list)))
        return SysWidget.get_active_order_list().handler(hander)

    def __active_order_commission(self, exclude_ref=None):
        hander = lambda order_list: sum(
            map(lambda order: self._commission(order.instrument, order.price, order.volume - order.filled_volume),
                filter(lambda order: order.order_ref != exclude_ref, order_list)))
        return SysWidget.get_active_order_list().handler(hander)

    def _margin(self, instrument, price, volume):
        return price * volume * get_trade_unit(instrument) * self._margin_rate(instrument)

    def _margin_rate(self, instrument):
        return 0.2

    def _commission(self, instrument, price, volume):
        return self._commission_rate(instrument) * price * volume * get_trade_unit(instrument)

    def _commission_rate(self, instrument):
        return 1.0 / 10000.0

    def get_instrument_position_profit(self, offset, instrument):
        shares = self.__shares.get_dict_shares()

        _temp = (self.__ticks.get(instrument).DayClose - shares[offset][instrument][1]) * shares[offset][instrument][
            0] * get_trade_unit(instrument)
        if offset == Shares.LONG:
            return _temp
        else:
            return 0 - _temp

    @property
    def position_profit(self):
        profit = 0
        shares = self.__shares.get_dict_shares()
        for offset in shares:
            for instrument in shares[offset]:
                profit += self.get_instrument_position_profit(offset, instrument)
        return profit

    @property
    def interests(self):
        rt = self.__account['Available'] + self.position_profit
        if self.__account['MaxInterests'] < rt:
            self.__account['MaxInterests'] = rt
            self.__save()
        return rt

    @property
    def draw_down_cash(self):
        rt = self.__account['MaxInterests'] - self.interests
        if rt > self.__account['MaxDrawdownCash']:
            self.__account['MaxDrawdownCash'] = rt
            self.__save()
        return rt

    @property
    def draw_down(self):
        draw_down = self.draw_down_cash / self.__account['MaxInterests']
        return draw_down

    @property
    def max_draw_down_cash(self):
        return self.__account['MaxDrawdownCash']

    @property
    def max_draw_down(self):
        return self.max_draw_down_cash / self.__account['MaxInterests']

    @property
    def cash_of_no_margin(self):
        return self.__account['Available']

    @property
    def cash(self):
        return self.get_cash_of_no_ref()

    def get_available(self, instrument):
        return self.cash / self._margin_rate(instrument)

    def get_cash_of_no_ref(self, order_ref=None):
        return self.__account['Available'] - self.__active_order_margin(
            order_ref) - self.__shares_margin() - self.__active_order_commission(order_ref)

    @property
    def frozen_commission(self):
        return self.__active_order_commission()

    @property
    def frozen_margin(self):
        return self.__active_order_margin()

    @property
    def curr_margin(self):
        return self.__shares_margin()

    @property
    def start_cash(self):
        return self.__account['Start']

    @property
    def commission(self):
        return self.__account['Commission']

    @property
    def close_profit(self):
        return self.__account['CloseProfit']

    def update_start_cash(self, cash_added):
        self.__lock.acquire()
        self.__account['Available'] += cash_added
        self.__account['Start'] += cash_added
        self.__account['MaxInterests'] += cash_added
        self.__save()
        self.__lock.release()
