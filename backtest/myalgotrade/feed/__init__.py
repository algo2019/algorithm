import datetime

from pyalgotrade import bar, barfeed, dataseries
from pyalgotrade.barfeed import csvfeed
from pyalgotrade.utils import csvutils

Frequency = barfeed.Frequency
default_datetime_format = "%Y-%m-%d %H:%M:%S"
default_frequency = Frequency.MINUTE

class RowParser(csvfeed.RowParser):
    def getFieldNames(self):
        # It is expected for the first row to have the field names.
        return None

    def getDelimiter(self):
        return ","

    def parseBar(self, csvRowDict):
        dateTime = datetime.datetime.strptime(csvRowDict["datetime"], default_datetime_format)
        o = float(csvRowDict['open'])
        h = float(csvRowDict['high'])
        l = float(csvRowDict['low'])
        c = float(csvRowDict['close'])
        volume = float(csvRowDict['volume'])
        return bar.BasicBar(dateTime, o, h, l, c, volume, c, default_frequency)


class GenericRowParser(csvfeed.GenericRowParser):
    default_column_names = {
        "datetime": "Date Time",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
        "adj_close": "Adj Close",
    }
    default_timezone = None
    default_daily_bar_time = None

    def __init__(self, column_names=None, datetime_format=None, frequency=None, timezone=None, daily_bar_time=None):
        column_names = column_names or self.default_column_names
        datetime_format = datetime_format or default_datetime_format
        frequency = frequency or default_frequency
        timezone = timezone or self.default_timezone
        daily_bar_time = daily_bar_time or self.default_daily_bar_time
        csvfeed.GenericRowParser.__init__(self, column_names, datetime_format, daily_bar_time, frequency, timezone)


class SqlserverRowParser(csvfeed.RowParser):
    def __init__(self, frequency=None):
        self.frequency = frequency or default_frequency

    def getDelimiter(self):
        return ','

    def getFieldNames(self):
        pass

    def parseBar(self, row):
        items = row.strip().split(self.getDelimiter())
        date_time = datetime.datetime.strptime(items[0], default_datetime_format)
        open_, high, low, close, vol = [float(item) for item in items[1:]]
        vol = int(vol)
        return bar.BasicBar(date_time, open_, high, low, close, vol, close, self.frequency)


class TradingTimeFileter(csvfeed.BarFilter):
    def __init__(self):
        csvfeed.BarFilter.__init__(self)
        self.trading_times = (
            (datetime.time(0, 0, 0), datetime.time(3, 0, 0)),
            (datetime.time(8, 58, 0), datetime.time(11, 30, 1)),
            (datetime.time(13, 0, 0), datetime.time(15, 0, 1)),
            (datetime.time(20, 58, 0), datetime.time(23, 59, 59))
        )

    def includeBar(self, bar_):
        return self.is_trading_time(bar_.getDateTime())

    def is_trading_time(self, day_time):
        time = day_time.time()
        for timezone in self.trading_times:
            if timezone[0] <= time <= timezone[1]:
                return True
        return False


class MultiFilter(csvfeed.BarFilter):
    def __init__(self):
        csvfeed.BarFilter.__init__(self)
        self._filters = {}
        self.add_filter('trading time', TradingTimeFileter())

    def includeBar(self, bar_):
        for filter in self._filters.values():
            if not filter.includeBar(bar_):
                return False
        return True

    def add_filter(self, name, filter):
        self._filters[name] = filter

    def remove_filter(self, name):
        if self._filters.get(name) is not None:
            del self._filters[name]
            return True
        return False


class Feed(csvfeed.BarFeed):
    def __init__(self, frequency=barfeed.Frequency.MINUTE):
        csvfeed.BarFeed.__init__(self, frequency, maxLen=dataseries.DEFAULT_MAX_LEN)

    def barsHaveAdjClose(self):
        return False

    def add_bars_from_csv(self, instrument, path, row_parser):
        reader = csvutils.FastDictReader(open(path, "r"), fieldnames=row_parser.getFieldNames(),
                                         delimiter=row_parser.getDelimiter())
        self.add_bars_from_mem(instrument, reader, row_parser)

    def addBarsFromCSV(self, *args, **kwargs):
        raise Exception('use add_bars_from_csv instead.')

    def add_bars_from_mem(self, instrument, values, row_parser):
        loaded_bars = []
        bar_filter = self.getBarFilter()
        for row in values:
            bar_ = row_parser.parseBar(row)

            if bar_ is not None and (bar_filter is None or bar_filter.includeBar(bar_)):
                loaded_bars.append(bar_)
        self.addBarsFromSequence(instrument, loaded_bars)
