from pyalgotrade.barfeed import OptimizerBarFeed


class FeedForPickle(object):
    def __init__(self, feed_dict):
        self.instruments_dict = {}
        self.bars_dict = {}
        self.frequency_dict = {}
        for bar_name, bar_feed in feed_dict.items():
            bars_value_list = []
            for datetime_, bars in bar_feed:
                bars_value_list.append(bars)
            instruments = bar_feed.getRegisteredInstruments()
            self.instruments_dict[bar_name] = instruments
            self.bars_dict[bar_name] = bars_value_list
            self.frequency_dict[bar_name] = bar_feed.getFrequency()

    def gen_feed_dict(self):
        feed_dict = {}
        for name in self.bars_dict.keys():
            feed_dict[name] = OptimizerBarFeed(self.frequency_dict[name],
                                               self.instruments_dict[name],
                                               self.bars_dict[name])
        return feed_dict
