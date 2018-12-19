from TradeEngine.GlobleConf import Shares
from TradeEngine.GlobleConf import OffSet
from TradeEngine.GlobleConf import TradeSide


class OrderUnit(object):
    def __init__(self, instrument, offset, trade_side, price, volume):
        self.__instrument = instrument
        self.price = float(price)
        self.__volume = int(volume)
        self.__trade_side = trade_side
        self.__offset = offset
        self.__attributes = ['price', 'volume', 'instrument', 'trade_side', 'offset']

    def add_copy_attributes(self, name):
        if type(name) == str:
            self.__attributes.append(name)
        elif type(name) in (list, type):
            self.__attributes = self.__attributes + name

    def is_long(self):
        return self.long_or_short == Shares.Long

    def is_short(self):
        return not self.is_long()

    def is_open(self):
        return self.__offset == OffSet.Open

    @property
    def long_or_short(self):
        if (self.is_buy() and self.is_open()) or (self.is_sell() and not self.is_open()):
            return Shares.Long
        return Shares.Short

    @property
    def trade_side(self):
        return self.__trade_side

    @property
    def offset(self):
        return self.__offset

    @property
    def volume(self):
        return self.__volume

    @property
    def instrument(self):
        return self.__instrument

    def is_buy(self):
        return self.trade_side == TradeSide.Buy

    def is_sell(self):
        return not self.is_buy()

    def copy_unit(self, **kwargs):
        for key in self.__attributes:
            if kwargs.get(key) is None:
                kwargs[key] = self.__getattribute__(key)
        try:
            return self.__class__(**kwargs)
        except:
            return OrderUnit(**kwargs)
