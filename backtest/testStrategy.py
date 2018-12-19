# coding=utf-8
import addAlgorithmEnginePath
import myalgotrade

from myalgotrade import strategy
from pyalgotrade.technical import ma
import multiprocessing


class SampleStrategy(strategy.StrategyBase):
    def __init__(self, bar_feed, log_path, params, cash):
        super(SampleStrategy, self).__init__(bar_feed, log_path, params, cash_or_brk=cash)
        self.instrument = bar_feed.getDefaultInstrument()  # InstrumentID
        short_days = int(params['ma_short'])  # average params
        long_days = int(params['ma_long'])
        self.price_ds = bar_feed[self.instrument].getCloseDataSeries()  # history data
        self.sma_short = ma.SMA(self.price_ds, short_days)  # A moving average sequence that is updated with the price sequence
        self.sma_long = ma.SMA(self.price_ds, long_days)

    # Returns a key based on the argument, which is used as the log name
    @classmethod
    def get_log_key(cls, params):
        return '-'.join(str(params[key]) for key in sorted(params.keys()))

    # Strategies to start
    def on_start(self):
        print 'start cash:', self.getBroker().getCash()

    # Strategies to stop
    def on_finish(self, bars):
        print 'end cash:', self.getBroker().getCash()

    # open success
    def on_enter_ok(self, position):
        entry_order = position.getEntryOrder()  # 该仓位的开仓orde
        output = '\t'.join(
            str(i) for i in ('enter', position.getInstrument(), position.getShares(), entry_order.getAvgFillPrice()))
        # self.info(output)

    # open failed
    def on_enter_canceled(self, position):
        print 'enter canceled!'

    # close success
    def on_exit_ok(self, position):
        exit_order = position.getExitOrder()
        output = '\t'.join(
            str(i) for i in ('exit', position.getInstrument(), position.getShares(), exit_order.getAvgFillPrice()))
        # self.info(output)

    # close failed
    def on_exit_canceled(self, position):
        print 'exit caneled!'
        position.exitMarket()  # To unwind

    # order status update
    def on_order_updated(self, order):
        pass

    # Each new bar data call is made once, and bars contains bars of all varieties at the same time
    def on_bars(self, bars):
        # print 'price:', bars[self.instrument].getClose()

        # Too little data to calculate the ema
        if self.sma_long[-1] is None:
            # print 'not enough bars for sma, skipped'
            return

        # Take all positions
        positions = list(self.getActivePositions())
        if len(positions) > 1:
            raise Exception('we should at most have one position in this strategy.')

        # Price is above average and short position, open long position
        if self.sma_short[-1] > self.sma_long[-1]:
            if len(positions) == 0:
                shares = 1
                self.enterLong(self.instrument, shares, True)  # open with market price

        # Price is below the average and there are positions, open positions
        elif self.sma_short[-1] < self.sma_long[-1]:
            if len(positions) == 1:
                position = positions[0]
                if not position.exitActive():
                    position.exitMarket()  # close with market price


# coding=utf-8
from datetime import datetime
from myalgotrade.util import dbutil
from myalgotrade.feed import Frequency, feed_manager
from myalgotrade import strategy
import multiprocessing
import pprint

# See the next cell for parameter definitions
def run_sample_sql(experiment_key, strategy_class, instrument, param, start, end, frequency, before_days=0):

    # Obtain the main contract period of this variety
    feed_infos = dbutil.get_dominant_contract_infos(instrument, frequency, start, end, before_days)
    print 'feed infos:'
    pprint.pprint(feed_infos)

    feed_mng = feed_manager.DataServerFeedManager(feed_infos) # feed manager
    feeds_dict = feed_mng.get_feeds_by_range(start, end) #get feed
    print 'feeds:'
    pprint.pprint(feeds_dict)

    # log key Used to identify back-test the log file at a time, using experiment_key + instrument here
    log_key = strategy.log_path_delimiter.join((experiment_key, instrument))
    result = strategy.run_strategy(strategy_class, feeds_dict, log_key, param, initial_cash=1000000, use_previous_cash=False)

#     process = multiprocessing.Process(target=result.analyze_result.plotEquityCurve, args=(log_key,))
#     process.start()  # Notebook cannot open multiple processes, running in other ides

    return result, log_key

args = dict(
    experiment_key = 'tutorial',            # The log identifier
    strategy_class = SampleStrategy,        # Policy class for backtesting
    param = {'ma_short': 5, 'ma_long':40},  # Strategy parameters
    start = datetime(2010, 2, 1),           # The start time
    end = datetime(2011, 12, 31),             # The end of time
    frequency = Frequency.DAY,      # The frequency of bar input, this is 10 minutes
    before_days = 0,                        # How many days before becoming the main contract to start collecting data
    # instrument = 'SR',                     # Varieties of commodities
)

result, log_key = run_sample_sql(instrument='SR', **args)