import datetime
from dataServer import dataServer
from pyalgotrade import bar
from pyalgotrade import dataseries
from pyalgotrade.barfeed import membf
from OnLineSysBar import Bar


class BarFeed(membf.BarFeed):
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, 'pickle'):
            return super(BarFeed, cls).__new__(BarFeed)
        else:
            return super(BarFeed, cls).__new__(_DataServerBarFeed, *args, **kwargs)

    def __init__(self, symbol=None, start=None, end=None, period='1d', before_day=0, after_day=0,
                 maxLen=dataseries.DEFAULT_MAX_LEN, logger=None):
        self.daily_bars = {}
        membf.BarFeed.__init__(self, bar.Frequency.DAY, maxLen)

    def getNextBars(self):
        bars = super(BarFeed, self).getNextBars()
        if bars is not None:
            for key in bars.keys():
                if self.daily_bars.get(key) is None:
                    self.daily_bars[key] = {
                        'open': dataseries.SequenceDataSeries(),
                        'close': dataseries.SequenceDataSeries(),
                        'high': dataseries.SequenceDataSeries(),
                        'low': dataseries.SequenceDataSeries(),
                        'volume': dataseries.SequenceDataSeries(),
                    }
                min_bar = bars[key]
                if min_bar.has_tag(Bar.tag_day_last):
                    self.daily_bars[key]['open'].appendWithDateTime(min_bar.DateTime, min_bar.DayOpen)
                    self.daily_bars[key]['close'].appendWithDateTime(min_bar.DateTime, min_bar['DClose'])
                    self.daily_bars[key]['high'].appendWithDateTime(min_bar.DateTime, min_bar['DHigh'])
                    self.daily_bars[key]['low'].appendWithDateTime(min_bar.DateTime, min_bar['DLow'])
                    self.daily_bars[key]['volume'].appendWithDateTime(min_bar.DateTime, min_bar['DVolume'])
        return bars

    def reset(self):
        super(BarFeed, self).reset()
        self.daily_bars = {}

    def barsHaveAdjClose(self):
        return False

    def pickle_dump(self, f):
        import cPickle
        cPickle.dump(self.getKeys(), f)
        cPickle.dump(self._BarFeed__bars, f)

    def _pickle_load(self, f):
        import cPickle
        for key in cPickle.load(f):
            self.registerDataSeries(key)
        self._BarFeed__bars = cPickle.load(f)
        for instrument in self._BarFeed__bars:
            self._BarFeed__nextPos.setdefault(instrument, 0)

    @classmethod
    def pickle_load(cls, f):
        setattr(cls, 'pickle', True)
        b = cls()
        b._pickle_load(f)
        return b


class _DataServerBarFeed(BarFeed):
    Periods = ['1d', '1m', '5m', '10m', '15m', '30m', '60m']

    def __init__(self, symbol, start, end, period='1d', before_day=0, after_day=0, maxLen=dataseries.DEFAULT_MAX_LEN,
                 logger=None):
        if logger is None:
            from pprint import pprint
            self.logger = pprint
        else:
            self.logger = logger
        self.__symbol = symbol
        self.__start = start
        self.__end = end
        self.__before_day = before_day
        self.__after_day = after_day
        if period == '1d':
            self.__period = period
        else:
            if period in self.Periods:
                self.__period = period
            else:
                raise Exception('%s period not support' % period)
        BarFeed.__init__(self, maxLen)
        self.addBarsFromDataServer()

    def __get_dom_info(self, d):
        d.start()
        conf = {
            'dataName': 'domInfo',
            'start': self.__start,
            'end': self.__end,
            'afterday': self.__after_day,
            'beforday': self.__before_day,
            'commodity': [self.__symbol],
        }
        data = d.wmm(conf)
        conf['afterday'] = 0
        conf['beforday'] = 0
        data2 = d.wmm(conf)
        now = datetime.datetime.now()
        for line in data + data2:
            if line[2].date() >= now.date():
                line[2] = d.tdaysoffset(1, now.date()).Data[0][0]

        symbol = self.__symbol[0:2].upper()
        if symbol in ['IH', 'IF', 'IC']:
            for line in data:
                line[1] = d.tdaysoffset(1, line[1]).Data[0][0]
            for line in data2:
                line[1] = d.tdaysoffset(1, line[1]).Data[0][0]
                line[2] = d.tdaysoffset(1, str(line[2]).split()[0]).Data[0][0]
        d.stop()
        return data, data2

    def __get_day_data(self, d, instrument, start, end):
        d.start()
        conf = {
            'dataName': 'data',
            'code': instrument,
            'fields': 'open,close,high,low,volume,limitup,limitdown',
            'start': start,
            'end': end,
            'includeend': True,
            'period': '1d',
            'adj': '0',
        }
        data = d.wmm(conf)
        d.stop()
        return data

    def __get_min_data(self, d, instrument, start, end):
        d.start()
        conf = {
            'dataName': 'data',
            'code': instrument,
            'fields': ['open', 'high', 'low', 'close', 'volume'],
            'start': start,
            'end': end,
            'tradingday': True,
            'includeend': True,
            'period': self.__period,
            'adj': '0',
        }
        data = d.wmm(conf)
        d.stop()
        return data

    def addBarsFromDataServer(self):
        dom_info, real_info = self.__get_dom_info(dataServer())
        self.logger("dom_info:")
        self.logger(dom_info)
        for i in xrange(len(dom_info)):
            instrument, start, end = dom_info[i]
            _, dom_start, dom_end = real_info[i]
            self.__add_one_day(instrument, start, end, dom_start, dom_end)

    def __add_one_day(self, instrument, start, end, dom_start, dom_end):
        i = 0
        for i in xrange(10):
            try:
                self.logger("get data of %s start" % instrument)
                d = dataServer()
                d.start()
                trading_days = [x.date() for x in d.tdays(d.tdaysoffset(2, start).Data[0][0], d.tdaysoffset(-2, end).Data[0][0]).Data[0]]
                d.stop()
                now = datetime.datetime.now()
                if end.date() >= now.date():
                    end = trading_days[trading_days.index(now.date()) - 1]
                min_data = self.__get_min_data(dataServer(), instrument, start, end)
                day_data = self.__get_day_data(dataServer(), instrument, start, end)
                self.logger("get data of %s end" % instrument)
            except Exception as e:
                self.logger(e)
                self.logger("get data of %s err, retry ..." % instrument)
                continue
            self.__add_bars(trading_days, min_data, day_data, dom_start, dom_end)
            break

        if i == 9:
            raise Exception("get data of %s err" % instrument)

    def __add_bars(self, trading_days, min_data, day_data, dom_start, dom_end):
        self.logger("add bars start")
        bars = {}
        md = min_data
        dd = day_data
        High = -1
        Low = float('inf')
        Volume = 0

        lineno = self.__get_data_line_no(trading_days, md, dd)
        mi, di = lineno.next()
        _bar = None
        tag_new_day = True
        while mi is not None:
            dt, ins, open, high, low, close, volume = md[mi]
            tdt, _, Open, d_close, d_high, d_low, d_volume, LimitUp, LimitDown = dd[di]
            ins = str(ins)
            if high > High:
                High = high
            if low < Low:
                Low = low
            Volume += volume

            c = {'volume': volume, 'open': open, 'high': high, 'low': low, 'period': self.__period, 'dateTime': dt,
                 'Volume': Volume, 'LastPrice': close, 'OpenPrice': Open, 'HighestPrice': High, 'LowestPrice': Low,
                 'AskPrice1': -1, 'AskVolume1': -1, 'BidPrice1': -1, 'BidVolume1': -1, 'TradingDay': str(tdt.date()),
                 'UpdateTime': str(dt.time()), 'ExchangeID': '-', 'UpperLimitPrice': LimitUp, 'close': close,
                 'LowerLimitPrice': LimitDown, 'OpenInterest': -1, 'SettlementPrice': -1, 'InstrumentID': ins,
                 'DHigh': d_high, 'DLow': d_low, 'DClose': d_close, 'DVolume': d_volume}

            if bars.get(ins) is None:
                bars[ins] = []
            _bar = Bar(c)

            if tag_new_day:
                tag_new_day = False
                _bar.set_tag(_bar.tag_day_first)

            if dom_start <= tdt <= dom_end:
                _bar.set_tag(_bar.tag_dom)

            od = di
            mi, di = lineno.next()
            if od != di:
                _bar.set_tag(_bar.tag_day_last)
                tag_new_day = True
                High = -1
                Low = float('inf')
                Volume = 0

            bars[ins].append(_bar)

        if _bar is not None:
            _bar.set_tag(_bar.tag_instrument_last)

        for key in bars:
            self.addBarsFromSequence(key, bars[key])
        self.logger("add bars end")

    @staticmethod
    def __get_data_line_no(trading_days, md, dd, mi=0, di=0):
        ddt = dd[di][0].date()
        while mi < len(md) and di < len(dd):
            mdt = md[mi][0].date()
            if mdt == ddt:
                if md[mi][0].time() > datetime.time(20):
                    di += 1
                    ddt = dd[di][0].date()
            elif mdt < ddt:
                if md[mi][0].time() >= datetime.time(8):
                    while not (trading_days.index(mdt) + 1 == trading_days.index(ddt)
                               and md[mi][0].time() > datetime.time(20)):
                        mi += 1
                        mdt = md[mi][0].date()
            else:
                while mdt > ddt:
                    di += 1
                    ddt = dd[di][0].date()

            yield mi, di
            mi += 1
        yield None, None
