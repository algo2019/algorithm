from TradeEngine.GlobleConf import SysWidget
from TradeEngine.GlobleConf import TradeSide, OffSet
from TradeEngine.TradeServer.OrderUnit import OrderUnit
import tradeutil
from .tradeclientfactory import Config


class InsertArgs(OrderUnit):
    def __init__(self, strategy_name, name, instrument, offset, trade_side, volume, price=None, time_out=0,
                 order_price_type='2', time_condition='3', contingent_condition='1', is_local=False):

        limit, price = self.get_market_price(price, instrument, trade_side)
        super(InsertArgs, self).__init__(str(instrument), offset, trade_side, price, volume)
        self.add_copy_attributes(
            ['strategy_name', 'name', 'time_out', 'order_price_type', 'time_condition', 'contingent_condition',
             'is_local'])
        self.__order_price_type = order_price_type
        self.__time_condition = time_condition
        self.__contingent_condition = contingent_condition
        self.__strategy_name = str(strategy_name)
        self.__name = name
        self.__time_out = int(time_out)
        self.is_local = is_local

    @staticmethod
    def get_market_price(price, instrument, trade_side):
        tick_data = SysWidget.get_tick_data().get(instrument)
        if tick_data is None:
            raise Exception('tick data not exists:%s' % instrument)
        if trade_side == TradeSide.Sell:
            if price is None:
                price = tick_data.DayClose - tradeutil.get_min_point(instrument) * Config.market_point
            else:
                price = float(price)
            if price <= tick_data.LowerLimitPrice:
                return [True, tick_data.LowerLimitPrice]
            else:
                return [False, price]
        else:
            if price is None:
                price = tick_data.DayClose + tradeutil.get_min_point(instrument) * Config.market_point
            else:
                price = float(price)
            if price >= tick_data.UpperLimitPrice:
                return [True, tick_data.UpperLimitPrice]
            else:
                return [True, price]

    @property
    def strategy_name(self):
        return self.__strategy_name

    @property
    def name(self):
        return self.__name

    @property
    def time_out(self):
        return self.__time_out

    @property
    def order_price_type(self):
        return self.__order_price_type

    @property
    def time_condition(self):
        return self.__time_condition

    @property
    def contingent_condition(self):
        return self.__contingent_condition

    def copy_args(self, **kwargs):
        return self.copy_unit(**kwargs)

    def __str__(self):
        return '%s %s %s %2.2f %d %d' % (
            self.instrument, OffSet.to_string(self.offset), TradeSide.to_string(self.trade_side), self.price,
            self.volume, self.time_out)
