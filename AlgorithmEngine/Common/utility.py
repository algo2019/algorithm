import datetime
from Common.Dao.DBDataDao import DBDataDao


class TradingTime(object):
    __TIMES = (
        (datetime.time(0, 0, 0), datetime.time(2, 30, 0)),
        (datetime.time(9, 0, 01), datetime.time(11, 30, 0)),
        (datetime.time(13, 30, 0), datetime.time(15, 0, 0)),
        (datetime.time(21, 0, 01), datetime.time(23, 59, 59, 999999)),
    )
    __CLOSE = (datetime.time(15, 0, 0), datetime.time(21, 0, 0))

    __db_dao = DBDataDao()

    @classmethod
    def times(cls):
        return cls.__TIMES

    @classmethod
    def is_trading(cls, date_time=None):
        if date_time is None:
            time = datetime.datetime.now().time()
        else:
            time = date_time.time()
        for range_ in cls.__TIMES:
            if range_[0] <= time < range_[1]:
                return True
        return False

    @classmethod
    def is_close(cls, date_time=None):
        if date_time is None:
            time = datetime.datetime.now().time()
        else:
            time = date_time.time()
        if cls.__CLOSE[0] <= time < cls.__CLOSE[1]:
            return True
        return False

    @classmethod
    def datetime_time_subtract(cls, minuend, subtrahend):
        return (60 * 60) * (minuend.hour - subtrahend.hour) + 60 * (minuend.minute - subtrahend.minute) + (minuend.second - subtrahend.second)

    @classmethod
    def next_trading_time_delay(cls, date_time=None):
        if date_time is None:
            time = datetime.datetime.now().time()
        else:
            time = date_time.time()
        for range_ in cls.__TIMES:
            if range_[0] <= time < range_[1]:
                return 0
            if range_[0] > time:
                return cls.datetime_time_subtract(range_[0], time)
        raise Exception('what happened ?')

    @classmethod
    def is_trading_day(cls):
        return cls.__db_dao.is_trading_day()

