import datetime

from pyalgotrade import bar
from pyalgotrade.dataseries import resampled

import myalgotrade.feed
from myalgotrade import strategy
from myalgotrade.broker import tradeutil


class DTStrategy(strategy.StrategyBase):
    default_one_stop_cash = 10000
    @classmethod
    def get_log_key(cls, params):
        return strategy.log_path_delimiter.join(
                str(params[key]) for key in ('k', 'm', 'trailing_start', 'stop_loss_set'))

    def __init__(self, bar_feed, log_path, params, cash):
        super(DTStrategy, self).__init__(bar_feed, log_path, params, cash_or_brk=cash)
        self.instrument = bar_feed.getDefaultInstrument()
        self.bar_ds = bar_feed[self.instrument]
        self.day_bars = []
        self.day_bar_grouper = None
        self.open_day = None
        self.position = None
        self.init_params(params)

    def info(self, msg):
        # super(DTStrategy, self).info(self.instrument + '\t' + msg)
        pass

    def init_params(self, params):
        self.upper_band = self.lower_band = None
        self.high_after_entry = -1
        self.low_after_entry = 99999999
        self._k = float(params['k']) / 10
        self._mday = params['m']
        self._trailing_start = params['trailing_start']
        self._stop_loss_set = params['stop_loss_set']
        self._adjust = params['adjust']
        self.min_point = tradeutil.get_min_point(self.instrument)
        self._trailing_stop = self._stop_loss_set + self._adjust
        self._lots = tradeutil.get_default_lots(self.instrument)
        # trade_unit=  tradeutil.get_trade_unit(self.instrument)
        # self.lots = int(self.default_one_stop_cash / (self.min_point * trade_unit * self._stop_loss_set))#tradeutil.get_default_lots(self.instrument)

    @property
    def lots(self):
        cash = self.getBroker().getEquity()
        price = self.bar_ds[-1].getClose()
        trade_unit = tradeutil.get_trade_unit(self.instrument)
        margin_ratio = tradeutil.get_margin_ratio(self.instrument)
        price = price * trade_unit * margin_ratio
        lots = int(cash * 0.8 / price)
        lots = self._lots
        # print cash, price, lots
        if lots <= 0:
             lots = 1
        return lots

    def is_new_trading_day(self):
        if len(self.bar_ds) == 1:
            return True
        now = self.bar_ds[-1].getDateTime()
        last = self.bar_ds[-2].getDateTime()
        if now.date() == last.date():
            return last.hour <= 19 < now.hour
        else:
            return 8 <= last.hour <= 19

    def resample_day_bars(self):
        is_new_day = self.is_new_trading_day()
        bar_ = self.bar_ds[-1]
        if is_new_day:
            if self.day_bar_grouper is not None:
                self.day_bars.append(self.day_bar_grouper.getGrouped())
            self.info('new day: %s' % (str(bar_.getDateTime())))
            self.day_bar_grouper = resampled.BarGrouper(bar_.getDateTime(), bar_, bar.Frequency.DAY)
            self.open_day = bar_.getOpen()
        else:
            self.day_bar_grouper.addValue(bar_)
        return is_new_day

    def update_high_low(self):
        high = self.bar_ds[-1].getHigh()
        low = self.bar_ds[-1].getLow()
        self.high_after_entry = max(self.high_after_entry, high)
        self.low_after_entry = min(self.low_after_entry, low)

    def update_band(self):
        self.info('update bande')
        hh = hc = 0
        ll = lc = 99999999
        for i in range(1, self._mday + 1):
            day_bar = self.day_bars[-i]
            hh = max(hh, day_bar.getHigh())
            hc = max(hc, day_bar.getClose())
            ll = min(ll, day_bar.getLow())
            lc = min(lc, day_bar.getClose())
        sell_range = buy_range = max(hh - lc, hc - ll)

        sell_trigger = self._k * sell_range
        buy_trigger = self._k * buy_range

        self.upper_band = self.open_day + buy_trigger
        self.lower_band = self.open_day - sell_trigger
        self.info('hh, ll, hc, lc: ' + '\t'.join('%.2f' % v for v in (hh, ll, hc, lc)))
        self.info('open:\t%.2f\trange:%.2f' % (self.open_day, sell_range))

        self.info('band:\t%.2f\t%.2f' % (self.upper_band, self.lower_band))

    def on_bars(self, bars):
        # return
        is_new_day = self.resample_day_bars()
        if len(self.day_bars) <= self._mday:
            return
        if is_new_day:
            self.update_band()
        self.update_high_low()
        instrument = bars.getInstruments()[0]
        price = bars[instrument].getPrice()
        price = self.bar_ds[-1].getPrice()
        last_price = self.bar_ds[-2].getPrice()
        buy_condition = (last_price < self.upper_band) and (price >= self.upper_band)
        sell_condition = (last_price > self.lower_band) and (price <= self.lower_band)

        if buy_condition and sell_condition:
            raise Exception('buy and sell condition at same time!')

        if self.position is None or self.position.getShares() == 0:
            if buy_condition:
                self.enterLong(self.instrument, self.lots, True)
            if sell_condition:
                self.enterShort(self.instrument, self.lots, True)
            return

        if len(self.getActivePositions()) > 1:
            raise Exception("more than one position")

        if not self.position.entryFilled():
            raise Exception("entry not filled")

        if self.position.getShares() > 0:
            if sell_condition:
                self.position.exitMarket(True)
                self.enterShort(self.instrument, self.lots, True)

            else:
                if self.high_after_entry >= self.entry_price + self._trailing_start * self.min_point:
                    steps = int((self.high_after_entry - self.entry_price) / (self._trailing_start * self.min_point))
                    stop_price = self.high_after_entry - steps * self._trailing_stop * self.min_point
                else:
                    stop_price = self.entry_price - self._stop_loss_set * self.min_point

                if price <= stop_price:
                    self.position.exitMarket(True)

        elif self.position.getShares() < 0:
            if buy_condition:
                self.position.exitMarket(True)
                self.enterLong(self.instrument, self.lots, True)

            else:
                if self.low_after_entry <= self.entry_price - self._trailing_start * self.min_point:
                    steps = int((self.entry_price - self.low_after_entry) / (self._trailing_start * self.min_point))
                    stop_price = self.low_after_entry + steps * self._trailing_stop * self.min_point
                else:
                    stop_price = self.entry_price + self._stop_loss_set * self.min_point
                if price >= stop_price:
                    self.position.exitMarket(True)

    def on_enter_ok(self, position):
        self.position = position
        order_price = position.getEntryOrder().getExecutionInfo().getPrice()
        self.entry_price = order_price
        self.high_after_entry = self.low_after_entry = self.entry_price
        quantity = position.getEntryOrder().getExecutionInfo().getQuantity()
        print '\t'.join(str(i) for i in ('enter', self.getBroker().getEquity(), order_price, quantity)), '\t',

    def on_enter_canceled(self, position):
        self.info('enter canceled.')

    def on_exit_ok(self, position):
        self.position = None
        price = position.getExitOrder().getExecutionInfo().getPrice()
        print '\t'.join(str(i) for i in ('exit', price, position.getPnL(), self.getBroker().getEquity()))

    def on_exit_canceled(self, position):
        position.exitMarket(True)
        self.info('exit canceled.')


def _param_generator_factory():
    count = 0
    for k in (4, 5, 6, 7, ):
        for m in (2, 3, 4, 5,):
            for stop_loss_set in (20, ):#(20, 30, 40, 50, 60):
                for ratio in (3,):#(1, 2, 3, 4):
                    trailing_start = stop_loss_set * ratio
                    count += 1
                    # print count

                    yield {
                        'k': k,
                        'm': m,
                        'trailing_start': trailing_start,
                        'stop_loss_set': stop_loss_set,
                        'adjust': 0,
                    }

def _param_generator_factory2():
    for k in xrange(5, 8, 10):
        for m in xrange(3, 8, 10):
            for trailing_start in xrange(20, 120, 20):
                for stop_loss_set in xrange(10, 50, 10):
                    if trailing_start < stop_loss_set:
                        continue
                    yield {
                        'k': k,
                        'm': m,
                        'trailing_start': trailing_start,
                        'stop_loss_set': stop_loss_set,
                        'adjust': 0,
                    }

dt_param_generator_factory = _param_generator_factory


def main():
    import cProfile
    import pprint
    import os
    from myalgotrade import util
    use_profile = False

    start = datetime.datetime.now()
    print 'started'
    # Load the yahoo feed from the CSV file
    test_feed = myalgotrade.feed.Feed()
    bar_filter = myalgotrade.feed.MultiFilter()
    # bar_filter.add_filter('date range',
    #                      csvfeed.DateRangeFilter(datetime.datetime(2015, 7, 1), datetime.datetime(2015, 8, 1)))
    test_feed.setBarFilter(bar_filter)
    if use_profile:
        cProfile.run("test_feed.add_bars_from_csv('ag', 'data/test_bar.csv', RowParser())")
    else:
        test_feed.add_bars_from_csv('ag', '../data/test_bar.csv', myalgotrade.feed.RowParser())

    feed = test_feed
    # Evaluate the strategy with the feed's bars.

    params = {
        'k': 5,
        'm': 3,
        'trailing_start': 60,
        'stop_loss_set': 20,
        'adjust': 0,
        'min_point': 1,
        'lots': 1
    }
    log_key = os.path.join(strategy.log_root, 'test_ori-broker2')
    myStrategy = DTStrategy(feed, log_key, params)
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
    if use_profile:
        cProfile.run('myStrategy.run()', 'profiling.out')
    else:
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
