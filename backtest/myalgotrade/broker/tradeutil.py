from myalgotrade import util
from pyalgotrade.broker.backtesting import Commission

_trade_unit_config = {

}

_margin_ratio_config = {

}

_min_point_config = {

}

_default_lots_config = {

}

all_commodity_set = []

from datetime import datetime
from datetime import timedelta
period_available = {
    'm': datetime(2010, 1, 1),
    'c': datetime(2015, 8, 1),
    'y': datetime(2010, 1, 1),
    'l': datetime(2010, 6, 1),
    'p': datetime(2010, 1, 1),  # 2010-2012/4 volumn:10w-20w
    'i': datetime(2014, 4, 1),
    'pp': datetime(2014, 10, 1),
    'jd': datetime(2014, 5, 1),
    'sr': datetime(2010, 1, 1),
    'ta': datetime(2010, 1, 1),
    'fg': datetime(2013, 2, 1),
    'rm': datetime(2010, 1, 1),
    'cu': datetime(2010, 1, 1),
    'al': datetime(2015, 11, 1),
    'zn': datetime(2014, 8, 1),  # 2015:10w+-
    'ni': datetime(2015, 5, 1),
    'au': datetime(2013, 8, 1),
    'ag': datetime(2012, 9, 1),
    'rb': datetime(2010, 1, 1),
    'bu': datetime(2015, 9, 1),
    'ru': datetime(2010, 1, 1),
    'if': datetime(2010, 1, 1),
    'ih': datetime(2010, 1, 1),
    'ic': datetime(2010, 1, 1),
}


class Commodity(object):
    def __init__(self, symbol, min_point, trade_unit, lots=0, add_to_universe=True):
        global _trade_unit_config
        global _min_point_config
        global _default_lots_config
        global all_commodity_set
        symbol = str.lower(symbol)
        _min_point_config[symbol] = min_point
        _trade_unit_config[symbol] = trade_unit
        if lots == 0:
            lots = int(100 / (min_point * trade_unit))
        _default_lots_config[symbol] = lots
        if add_to_universe:
            all_commodity_set.append(symbol)


i = Commodity('i', 0.5, 100)
pp = Commodity('pp', 1, 5)
m = Commodity('m', 1, 10)
l = Commodity('l', 5, 5)
p = Commodity('p', 2, 10)
y = Commodity('y', 2, 10)
c = Commodity('c', 1, 10)
j = Commodity('j', 0.5, 100)
cs = Commodity('cs', 1, 10)
jm = Commodity('jm', 0.5, 60)
# ---
jd = Commodity('jd', 1, 10)

ma = Commodity('ma', 1, 10)
sr = Commodity('sr', 1, 10)
rm = Commodity('rm', 1, 10)
ta = Commodity('ta', 2, 5)
cf = Commodity('cf', 5, 5)
fg = Commodity('fg', 1, 20)
zc = Commodity('zc', 0.2, 100)

rb = Commodity('rb', 1, 10)
bu = Commodity('bu', 2, 10)
ni = Commodity('ni', 10, 1)
ru = Commodity('ru', 5, 10)
ag = Commodity('ag', 1, 15)
cu = Commodity('cu', 10, 5)
zn = Commodity('zn', 5, 5)
au = Commodity('au', 0.05, 1000)
al = Commodity('al', 5, 5)
IF = Commodity('if', 0.2, 300)
ic = Commodity('ic', 0.2, 200)
ih = Commodity('ih', 0.2, 300)


def get_trade_unit(instrument_or_symbol):
    symbol = util.get_symbol_by_insrument(instrument_or_symbol)
    return _get_trade_unit_by_symbol(symbol)


def _get_trade_unit_by_symbol(symbol):
    return _trade_unit_config.get(symbol, 10)


class BasicCommission(Commission):
    fee_rate = 0.0001

    def __init__(self):
        super(BasicCommission, self).__init__()

    def calculate(self, order, price, quantity):
        instrument = order.getInstrument()
        return self.calculate_commission(instrument, price, quantity)

    def calculate_commission(self, instrument, price, quantity):
        total = price * quantity * get_trade_unit(instrument)
        commission = total * self.fee_rate
        return commission


def get_margin_ratio(instrument_or_symbol):
    symbol = util.get_symbol_by_insrument(instrument_or_symbol)
    return _get_margin_by_symbol(symbol)


def _get_margin_by_symbol(symbol):
    return _margin_ratio_config.get(symbol, 1.0)


def get_min_point(instrument_or_symbol):
    symbol = util.get_symbol_by_insrument(instrument_or_symbol)
    return _get_min_point_by_symbol(symbol)


def _get_min_point_by_symbol(symbol):
    return _min_point_config.get(symbol, 1)


def get_default_lots(instrument_or_symbol):
    symbol = util.get_symbol_by_insrument(instrument_or_symbol)
    return _get_default_lots_by_symbol(symbol)


def _get_default_lots_by_symbol(symbol):
    return _default_lots_config.get(symbol, 1)


def get_available_start(instrument_or_symbol):
    symbol = util.get_symbol_by_insrument(instrument_or_symbol)
    # set available date to tomorrow when not available.
    return period_available.get(symbol, datetime.now() + timedelta(days=1))


def main():
    import pprint
    pprint.pprint(_default_lots_config)

if __name__ == '__main__':
    main()
