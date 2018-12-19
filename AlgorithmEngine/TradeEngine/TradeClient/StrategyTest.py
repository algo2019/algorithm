# coding=utf-8
from TradeEngine.CoreEngine import get_core_engine
from TradeEngine.OnBarDataStruct import OnBarData


# 切勿在正式上线文件中引用此文件

def pre_test(func):
    from TradeEngine.GlobleConf import Sys
    Sys.Debug = True
    from TradeEngine.TradeClient import BaseStrategy
    from TradeEngine.TradeClient import TestBaseStrategy
    BaseStrategy.BaseStrategy = TestBaseStrategy.BaseStrategy
    return func


@pre_test
def test_strategy(strategy_name, strategy_class, strategy_conf):
    CoreEngine = get_core_engine('ANALOG', strategy_name)
    core_engine = CoreEngine({'StrategyName': strategy_name, 'configs': strategy_conf})
    core_engine.start_engine(strategy_class)


def emit_data(instruments, period, start, end, time_delay=0.1):
    from dataServer import dataServer
    from TradeEngine.TradeClient.TestBaseStrategy import MarketData
    d = dataServer()
    d.start()
    fields = 'open,high,low,close,volume'
    field_list = fields.split(',')

    class T(object):
        hig, lo = 0, float('inf')

    def data(line, day_open, new):
        contest = {}
        i = 2
        for key in field_list:
            contest[key] = line[i]
            i += 1
        if new:
            T.hig = contest['high']
            T.lo = contest['low']
        else:
            T.hig = max(T.hig, contest['high'])
            T.lo = min(T.lo, contest['low'])

        contest['InstrumentID'] = line[1]
        contest['UpdateTime'] = line[0].strftime('%H:%M:%S')
        contest['dateTime'] = line[0].strftime('%Y-%m-%d %H:%M:%S')
        contest['period'] = period
        contest['Volume'] = -1
        contest['LastPrice'] = contest['close']
        contest['OpenPrice'] = day_open
        contest['HighestPrice'] = T.hig
        contest['LowestPrice'] = T.lo
        contest['AskPrice1'] = -1
        contest['AskVolume1'] = -1
        contest['BidPrice1'] = -1
        contest['BidVolume1'] = -1
        contest['TradingDay'] = None
        contest['ExchangeID'] = None
        contest['UpperLimitPrice'] = float('inf')
        contest['LowerLimitPrice'] = -float('inf')
        contest['OpenInterest'] = 0
        contest['SettlementPrice'] = 0
        return OnBarData(contest)

    for instrument in instruments:
        conf = {
            'dataName': 'data',
            'start': start,
            'end': end,
            'code': instrument,
            'fields': fields,
            'adj': '0',
            'period': period,
        }
        min_ = d.wmm(conf)

        conf = {
            'dataName': 'data',
            'start': start,
            'end': end,
            'code': instrument,
            'fields': 'open',
            'adj': '0',
            'period': '1d',
        }
        day = d.wmm(conf)

        i = 0
        j = 0
        maxl = len(day)
        while j < len(min_) and i < len(day):
            day_dt = day[i][0]
            line = min_[j]
            new = False
            min_dt = line[0]

            if min_dt.day == day_dt.day:
                if min_dt.hour > 15:
                    i += 1
                    day_dt = day[i][0]
                    new = True

            while min_dt.day > day_dt.day or (min_dt.day == day_dt.day and min_dt.hour > 16):
                i += 1
                if i >= maxl:
                    return
                day_dt = day[i][0]

            while min_dt.day + 1 < day_dt.day or (min_dt.day + 1 == day_dt.day and min_dt.hour < 16):
                j += 1
                line = min_[j]
                min_dt = line[0]

            print 'emit data', new, 'min', min_dt, 'day', day_dt
            MarketData.emit(instrument, data(line, day[i][2], new))
            if not new:
                j += 1

