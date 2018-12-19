# coding=utf-8
from myalgotrade import strategy
from pyalgotrade.technical import ma
import multiprocessing
import pprint
import pandas as pd
from pyalgotrade.technical import  bollinger

class SampleStrategy(strategy.StrategyBase):
    def __init__(self, bar_feed, log_path, params, cash, ouput_log=True):
        super(SampleStrategy, self).__init__(bar_feed, log_path, params, cash_or_brk=cash, ouput_log=ouput_log)
        self.instrument = bar_feed.getDefaultInstrument()  # 合约名
        short_days = int(params['ma_short'])  # 均线参数
        long_days = int(params['ma_long'])
        self.price_ds = bar_feed[self.instrument].getCloseDataSeries()  # 历史价格序列
        self.sma_short = ma.SMA(self.price_ds, short_days)  # 均线序列,随价格序列更新而更新
        self.sma_long = ma.SMA(self.price_ds, long_days)
        self.start_equity = self.getBroker().getEquity()

    # 根据参数返回一个key, 用作log名
    @classmethod
    def get_log_key(cls, params):
        return '-'.join(str(params[key]) for key in sorted(params.keys()))


    # 策略开始
    def on_start(self):
        print 'start cash:', self.getBroker().getCash()

    # 策略结束
    def on_finish(self, bars):
        print 'end cash:', self.getBroker().getCash()



    # 开仓成功
    def on_enter_ok(self, position):
        entry_order = position.getEntryOrder()  # 该仓位的开仓orde
        output = '\t'.join(
            str(i) for i in ('enter', position.getInstrument(), position.getShares(), entry_order.getAvgFillPrice()))
        # self.info(output)
        self.log_data('enter', entry_order.getAvgFillPrice())

    # 开仓失败
    def on_enter_canceled(self, position):
        print 'enter canceled!'

    # 平仓成功
    def on_exit_ok(self, position):
        exit_order = position.getExitOrder()
        output = '\t'.join(
            str(i) for i in ('exit', position.getInstrument(), position.getShares(), exit_order.getAvgFillPrice()))
        # self.info(output)
        self.log_data('exit', exit_order.getAvgFillPrice())

    # 平仓失败
    def on_exit_canceled(self, position):
        print 'exit caneled!'
        position.exitMarket()  # 重新平仓

    # 订单状态更新
    def on_order_updated(self, order):
        pass

    # 每个新bar数据调用一次, bars包含相同时间内所有品种的bar
    def on_bars(self, bars):
        # print 'price:', bars[self.instrument].getClose()
        bar = bars[self.instrument]
        self.log_data('open', bar.getOpen())
        self.log_data('high', bar.getHigh())
        self.log_data('low', bar.getLow())
        self.log_data('close', bar.getClose())
        self.log_data('sma_long', self.sma_long[-1])
        self.log_data('sma_short', self.sma_short[-1])
        self.log_data('profit', self.getBroker().getEquity() - self.start_equity)
        self.log_data('volume', bar.getVolume())

        # 数据太少,无法计算均线
        if self.sma_long[-1] is None:
            # print 'not enough bars for sma, skipped'
            return

        # 获取所有仓位
        positions = list(self.getActivePositions())
        if len(positions) > 1:
            raise Exception('we should at most have one position in this strategy.')

        # 价格位于均线之上 且 空仓, 开多仓
        if self.sma_short[-1] > self.sma_long[-1]:
            if len(positions) == 0:
                shares = 1
                self.enterLong(self.instrument, shares, True)  # 市价开仓

        # 价格位于均线之下 且 有仓位, 平仓
        elif self.sma_short[-1] < self.sma_long[-1]:
            if len(positions) == 1:
                position = positions[0]
                if not position.exitActive():
                    position.exitMarket()  # 市价平仓


def example_sql_dt(instrument):
    from datetime import datetime
    from myalgotrade.util import dbutil
    from myalgotrade.feed import Frequency, feed_manager
    from myalgotrade import strategy
    import multiprocessing
    import pprint

    start_date = datetime(2014, 2, 26)
    end_date = datetime(2014, 6, 19)

    feed_infos = dbutil.get_dominant_contract_infos(instrument, Frequency.MINUTE * 60, start_date, end_date, 0)
    print 'feed infos:'
    pprint.pprint(feed_infos)

    experiment_key = 'tutorial'
    feed_mng = feed_manager.SqlserverFeedManager(feed_infos)
    param = {
        'ma_short': 5,
        'ma_long': 40,
    }
    feeds_dict = feed_mng.get_feeds_by_range(start_date, end_date)
    print 'feeds:'
    pprint.pprint(feeds_dict)

    strategy_class = SampleStrategy
    log_key = strategy.log_path_delimiter.join((experiment_key, instrument))
    result = strategy.run_strategy(strategy_class, feeds_dict, log_key, param, initial_cash=1000000,
                                   use_previous_cash=False)

    # process = multiprocessing.Process(target=result.analyze_result.plotEquityCurve, args=(log_key,))
    # process.start()

    return result, log_key


if __name__ == '__main__':
    from myalgotrade.broker import tradeutil

    # process_list = []
    for instrument in ('SR',):  # '['SR', 'L', 'P', 'M', 'RB', 'RU']:  # tradeutil.all_commodity_set:
        result, log_key = example_sql_dt(str.upper(instrument))
        print log_key
        result = result.analyze_result
        # process = multiprocessing.Process(target=result.plotEquityCurve, args=(log_key,))
        # process.start()
    print 'done'
