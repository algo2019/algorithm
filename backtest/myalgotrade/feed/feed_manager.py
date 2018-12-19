import datetime

from pyalgotrade.barfeed import csvfeed

import myalgotrade.feed


def func_single_feed_getter(instrument, csv_path, frequency, row_parser):
    def get_feeds_by_date_range(start, end):
        feed_dict = {}
        feed = load_csv_feed(instrument, csv_path, frequency, row_parser)
        feed_dict[instrument] = feed
        return feed_dict

    return get_feeds_by_date_range


def load_csv_feed(instrument, path, frequency, row_parser, start_datetime=None, end_datetime=None):
    feed = myalgotrade.feed.Feed(frequency)
    bar_filter = myalgotrade.feed.MultiFilter()
    if start_datetime is not None or end_datetime is not None:
        if start_datetime is None or end_datetime is None:
            raise Exception('must set both start and end.')
        bar_filter.add_filter('date range', csvfeed.DateRangeFilter(start_datetime, end_datetime))
    feed.setBarFilter(bar_filter)
    feed.add_bars_from_csv(instrument, path, row_parser)
    return feed


class BaseFeedManager(object):
    def __init__(self):
        pass

    def get_feeds_by_range(self, start_datetime, end_datetime, instruments=None):
        raise NotImplementedError()

    def get_feeds_by_instruments(self):
        raise NotImplementedError()

    def get_all_feeds_instrument(self):
        raise NotImplementedError()


class CsvFeedManager(BaseFeedManager):
    def __init__(self, csv_infos=None):
        super(CsvFeedManager, self).__init__()
        self.feed_infos = {}
        if csv_infos is not None:
            self.add_csv_feeds(csv_infos)

    def add_feed(self):
        pass

    def add_csv_feed(self, instrument, path, frequency, row_parser):
        self.feed_infos[instrument] = (path, frequency, row_parser)

    def add_csv_feeds(self, csv_infos):
        for instrument, info in csv_infos.items():
            self.add_csv_feed(instrument, *info)

    def get_feeds_by_range(self, start_datetime, end_datetime, instruments=None):
        ret_dict = {}
        for instrument, info in self.feed_infos.items():
            if instruments is None or instrument in instruments:
                path, frequency, row_parser = info
                feed = load_csv_feed(instrument, path, frequency, row_parser, start_datetime, end_datetime)
                ret_dict[instrument] = feed
        return ret_dict

    def get_feeds_by_instruments(self, instruments=None):
        return self.get_feeds_by_range(None, None, instruments)

    def get_all_feeds_instrument(self):
        return self.feed_infos.keys()


from myalgotrade.util import dbutil

from myalgotrade import dataServerFeed

class DataServerFeedManager(BaseFeedManager):
    def __init__(self, feed_infos=None):
        super(DataServerFeedManager, self).__init__()
        self.feed_infos = {}
        if feed_infos is not None:
            self.add_feed_infos(feed_infos)

    def add_feed_info(self, instrument, frequency, start_datetime, end_datetime):
        self.feed_infos[instrument] = (frequency, start_datetime, end_datetime)

    def add_feed_infos(self, feed_infos):
        for instrument, info in feed_infos.items():
            self.add_feed_info(instrument, *info)

    def get_feeds_by_range(self, start_datetime, end_datetime, instrument_fileter=None):
        qry_infos = {}
        for instrument, info in self.feed_infos.items():
            if instrument_fileter is None or instrument in instrument_fileter:
                frequency, total_start_datetime, total_end_datetime = info
                qry_infos[instrument] = (
                    frequency,
                    max(start_datetime, total_start_datetime),
                    min(end_datetime, total_end_datetime)
                )
        feed_dict = {}
        for instrument, info in qry_infos.items():
            frequency, start, end = info
            if start >= end:
                continue
            period = dataServerFeed.get_period_str(frequency)
            feed = dataServerFeed.dataServerFeed(instrument, start, end, period)
            if not feed.eof():
                feed_dict[instrument] = feed
        return feed_dict


class SqlserverFeedManager(BaseFeedManager):
    def __init__(self, feed_infos=None):
        super(SqlserverFeedManager, self).__init__()
        self.sql_feed_infos = {}
        if feed_infos is not None:
            self.add_sqlserver_feeds(feed_infos)

    def add_sqlserver_feed(self, instrument, frequency, start_datetime, end_datetime):
        self.sql_feed_infos[instrument] = (frequency, start_datetime, end_datetime)

    def add_sqlserver_feeds(self, feed_infos):
        for instrument, info in feed_infos.items():
            self.add_sqlserver_feed(instrument, *info)

    def get_feeds_by_range(self, start_datetime, end_datetime, instruments=None):
        qry_infos = {}
        for instrument, info in self.sql_feed_infos.items():
            if instruments is None or instrument in instruments:
                frequency, total_start_datetime, total_end_datetime = info
                qry_infos[instrument] = (
                    frequency,
                    max(start_datetime, total_start_datetime),
                    min(end_datetime, total_end_datetime)
                )
        feed_datas = dbutil.get_data_from_sqlserver(qry_infos, async=True)
        # print 'qry_infos'
        # pprint.pprint(qry_infos)
        # print 'feed_datas'
        # pprint.pprint(feed_datas)
        feed_dict = {}
        for instrument in feed_datas:
            if len(feed_datas[instrument]) > 0:
                frequency = qry_infos[instrument][0]
                feed = myalgotrade.feed.Feed(frequency)
                feed.setBarFilter(myalgotrade.feed.MultiFilter())
                feed.add_bars_from_mem(instrument, feed_datas[instrument], myalgotrade.feed.SqlserverRowParser(frequency))
                feed_dict[instrument] = feed
        return feed_dict

    def get_feeds_by_instruments(self, instruments=None):
        return self.get_feeds_by_range(datetime.datetime(1990, 1, 1), datetime.datetime.now(), instruments)

    def get_all_feeds_instrument(self):
        return self.sql_feed_infos.keys()


def main():
    import datetime
    import pprint
    start_date = datetime.datetime(2014, 1, 1)
    end_date = datetime.datetime(2015, 6, 1)
    # feed_infos = dbutil.get_dominant_contract_infos('L', myalgotrade.feed.Frequency.MINUTE, start_date, end_date,
    #                                                5)
    feed_infos = {'L1405': (60,
                            datetime.datetime(2013, 12, 25, 0, 0),
                            datetime.datetime(2014, 3, 13, 0, 0)),
                  'L1409': (60,
                            datetime.datetime(2014, 3, 6, 0, 0),
                            datetime.datetime(2014, 7, 24, 0, 0)),
                  'L1501': (60,
                            datetime.datetime(2014, 7, 17, 0, 0),
                            datetime.datetime(2014, 12, 2, 0, 0)),
                  'L1505': (60,
                            datetime.datetime(2014, 11, 25, 0, 0),
                            datetime.datetime(2015, 3, 25, 0, 0)),
                  'L1509': (60,
                            datetime.datetime(2015, 3, 18, 0, 0),
                            datetime.datetime(2015, 5, 29, 0, 0))}

    pprint.pprint(feed_infos)
    print 'start', datetime.datetime.now()
    fm = SqlserverFeedManager(feed_infos)
    # fm = DataServerFeedManager(feed_infos)
    feeds = fm.get_feeds_by_range(start_date, end_date)
    print 'done', datetime.datetime.now()
    pprint.pprint(dict((instrument, feeds[instrument]) for instrument in feeds))


if __name__ == '__main__':
    main()
