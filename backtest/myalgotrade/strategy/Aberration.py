from pyalgotrade.technical import bollinger
from pyalgotrade.technical import cross

from myalgotrade import strategy
from myalgotrade.feed import Frequency


class Aberration(strategy.StrategyBase):
    @classmethod
    def get_log_key(cls, params):
        return strategy.log_path_delimiter.join(str(params[key]) for key in params)

    def __init__(self, bar_feed, log_path, params):
        super(Aberration, self).__init__(bar_feed, log_path, params)
        self.instrument = bar_feed.getDefaultInstrument()
        self.position = None

        self.feed_five_min = self.resampleBarFeed(Frequency.MINUTE * 5, self.on_bars_five_min)
        self.feed_five_min[self.instrument].setMaxLen(50)
        self.prices_five_min = self.feed_five_min[self.instrument].getCloseDataSeries()

        self.boll_period = params['boll_period']
        self.num_std_dev = params['num_std_dev']

        self.boll = bollinger.BollingerBands(self.prices_five_min, self.boll_period, self.num_std_dev)
        self.entry_price = 0
        self.highest_after_entry = 0
        self.lowest_after_entry = 0

        self.lots = 1
        self.stop_loss = 50
        self.take_profit1 = 200
        self.take_profit1_percent = 0.9
        self.take_profit2 = 160
        self.take_profit2_percent = 0.8
        self.take_profit3 = 100
        self.take_profit3_percent = 0.6


    def update_high_and_low(self, high_price, low_price):
        self.highest_after_entry = max(self.highest_after_entry, high_price)
        self.lowest_after_entry = min(self.lowest_after_entry, low_price)

    def on_enter_ok(self, position):
        self.position = position
        order_price = position.getEntryOrder().getExecutionInfo().getPrice()
        self.entry_price = order_price
        self.highest_after_entry = self.lowest_after_entry = self.entry_price

    def on_enter_canceled(self, position):
        self.info('enter canceled.')

    def on_exit_ok(self, position):
        self.position = None

    def on_exit_canceled(self, position):
        position.exitMarket(True)
        self.info('exit canceled.')

    def on_bars(self, bars):
        if self.position is None or self.position.getShares() == 0:
            return
        high_price = bars[self.instrument].getHigh()
        low_price = bars[self.instrument].getLow()
        close_price = bars[self.instrument].getClose()
        self.update_high_and_low(high_price, low_price)
        if self.position is not None and self.position.getShares() > 0:
            if self.lowest_after_entry <= self.entry_price - self.stop_loss:
                self.position.exitMarket()
            elif self.highest_after_entry >= self.entry_price + self.take_profit1 \
                    and close_price - self.entry_price <= (self.highest_after_entry
                                                               - self.entry_price) * self.take_profit1_percent:
                self.position.exitMarket()
            elif self.highest_after_entry >= self.entry_price + self.take_profit2 \
                    and close_price - self.entry_price <= (self.highest_after_entry
                                                               - self.entry_price) * self.take_profit2_percent:
                self.position.exitMarket()
            elif self.highest_after_entry >= self.entry_price + self.take_profit3 \
                    and close_price - self.entry_price <= (self.highest_after_entry
                                                               - self.entry_price) * self.take_profit3_percent:
                self.position.exitMarket()

        if self.position is not None and self.position.getShares() < 0:
            if self.highest_after_entry >= self.entry_price + self.stop_loss:
                self.position.exitMarket()
            elif self.lowest_after_entry <= self.entry_price - self.take_profit1 \
                    and (self.entry_price - close_price) <= (self.entry_price
                                                                 - self.lowest_after_entry) * self.take_profit1_percent:
                self.position.exitMarket()
            elif self.lowest_after_entry <= self.entry_price - self.take_profit2 \
                    and (self.entry_price - close_price) <= (self.entry_price
                                                                 - self.lowest_after_entry) * self.take_profit2_percent:
                self.position.exitMarket()
            elif self.lowest_after_entry <= self.entry_price - self.take_profit3 \
                    and (self.entry_price - close_price) <= (self.entry_price
                                                                 - self.lowest_after_entry) * self.take_profit3_percent:
                self.position.exitMarket()

    def on_bars_five_min(self, datetime, bars):
        # print bars.getDateTime(), bars[self.__instrument].getOpen(), bars[self.__instrument].getHigh(),\
        #     bars[self.__instrument].getLow(), bars[self.__instrument].getClose()
        buy_condition = cross.cross_above(self.prices_five_min, self.boll.getUpperBand())
        sell_condition = cross.cross_below(self.prices_five_min, self.boll.getLowerBand())

        if self.position is None or self.position.getShares() == 0:
            if buy_condition:
                self.enterLong(self.instrument, self.lots, True)
            if sell_condition:
                self.enterShort(self.instrument, self.lots, True)
            return

        if self.position.getShares() > 0:
            if sell_condition:
                self.position.exitMarket(True)
                self.enterShort(self.instrument, self.lots, True)

        if self.position.getShares() < 0:
            if buy_condition:
                self.position.exitMarket(True)
                self.enterLong(self.instrument, self.lots, True)


def _param_generator_factory():
    for boll_period in xrange(40, 60, 10):
        for num_std_dev in xrange(3, 5, 1):
            yield {'boll_period': boll_period, 'num_std_dev': num_std_dev}


param_generator_factory = _param_generator_factory



def main():
    import datetime
    import os
    import pprint
    from myalgotrade import util
    from myalgotrade import feed

    start = datetime.datetime.now()
    print 'started'
    # Load the yahoo feed from the CSV file
    test_feed = feed.Feed()
    bar_filter = feed.MultiFilter()
    # bar_filter.add_filter('date range',
    #                      csvfeed.DateRangeFilter(datetime.datetime(2015, 7, 1), datetime.datetime(2015, 8, 1)))
    test_feed.setBarFilter(bar_filter)
    test_feed.addBarsFromCSV('ag', '../data/test_bar.csv', feed.RowParser())

    # Evaluate the strategy with the feed's bars.

    params = {'boll_period': 50, 'num_std_dev': 3}
    log_key = os.path.join(strategy.log_root, 'test_ori-broker3')
    myStrategy = Aberration(test_feed, log_key, params)
    #
    # # Attach a returns analyzers to the strategy.
    # returnsAnalyzer = returns.Returns()
    # myStrategy.attachAnalyzer(returnsAnalyzer)
    #
    # # Attach the plotter to the strategy.
    # plt = plotter.StrategyPlotter(myStrategy)
    #
    # # Plot the simple returns on each bar.
    # plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

    # Run the strategy.



    mid = datetime.datetime.now()
    myStrategy.run()

    result = myStrategy.get_strategy_record()
    pprint.pprint(result)

    # myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

    # Plot the strategy.
    # plt.plot()

    result.analyze()
    p = util.show_analyze_result_process(result.analyze_result)
    end = datetime.datetime.now()
    print 'total:', end - start
    print 'load:', mid - start
    print 'run time:', end - mid


if __name__ == '__main__':
    main()


