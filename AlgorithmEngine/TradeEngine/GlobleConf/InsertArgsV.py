
class OffSet(object):
    Open = '0'
    Close = '1'
    CloseToday = '3'

    @classmethod
    def to_string(cls, offset):
        if offset == cls.Open:
            return 'open'
        elif offset == cls.Close:
            return 'close'
        elif offset == cls.CloseToday:
            return 'close_today'


class TradeSide(object):
    Buy = '0'
    Sell = '1'

    @classmethod
    def to_string(cls, ts):
        if ts == cls.Buy:
            return 'buy'
        elif ts == cls.Sell:
            return 'sell'


class Shares(object):
    Today = '0'
    Yesterday = '1'
    Long = '0'
    Short = '1'

    @classmethod
    def toString(cls, LorS):
        if LorS == cls.Long:
            return 'buy'
        elif LorS == cls.Short:
            return 'sell'

