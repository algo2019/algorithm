# coding=utf-8
from pyalgotrade.technical import highlow, ma
from datetime import datetime
from myalgotrade.util import dbutil
from myalgotrade.feed import Frequency, feed_manager
from myalgotrade import strategy
from myalgotrade.broker import tradeutil
import multiprocessing
from pyalgotrade.strategy import *
import pprint

# 基本版本，存在止盈止损模块，可过夜持仓

class Enum(object):
    def __init__(self, name, values):
        for value in values.strip().split():
            setattr(self, value, value)


class RBreaker(strategy.StrategyBase):
    def __init__(self, bar_feed, log_path, params, cash):
        super(RBreaker, self).__init__(bar_feed, log_path, params, cash_or_brk=cash)
        self.instrument = bar_feed.getDefaultInstrument()
        self.o_close_ds = bar_feed[self.instrument].getCloseDataSeries()
        self.b_break = -1
        self.s_setup = -1
        self.b_setup = -1
        self.s_enter = -1
        self.b_enter = -1
        self.s_break = -1
        self.pre_status = -1  # 1 为介于s_setup和b_break,2为介于b_setup与s_break之间，其他为-1
        self.buy_top_point = -1
        self.sell_low_point = -1
        self.stop_point = int(params['profit_stop_point']) * tradeutil.get_min_point(str.lower(self.instrument))
        self.break_factor = float(params['break_factor'])
        self.rev_factor = float(params['rev_factor'])
        resample_frequency = int(params['resample_frequency'])
        r_feed = self.resampleBarFeed(resample_frequency, self.resample_callback)

        self.r_open_ds = r_feed[self.instrument].getOpenDataSeries()
        self.r_close_ds = r_feed[self.instrument].getCloseDataSeries()
        self.r_high_ds = r_feed[self.instrument].getHighDataSeries()
        self.r_low_ds = r_feed[self.instrument].getLowDataSeries()
        window_size = int(params['window_size'])
        self.r_high = ma.SMA(self.r_high_ds, window_size)
        self.r_low = ma.SMA(self.r_low_ds, window_size)
        self.r_close = ma.SMA(self.r_close_ds, window_size)
        self.init_params()

    def init_params(self):
        self.TRADE_TYPE = Enum('TRADE_TYPE', 'NAN BUY SELL STOP')
        self.POSITION_STATUS = Enum('POSITION_STATUS', 'NAN LONG SHORT')
        self.candy_info = [[], [], [], [], []]
        self.plot_info = [[], [], [], [], [], [], []]
        self.plot_info_name = ['pivot_point', 'b_break', 's_setup', 's_enter', 'b_enter', 'b_setup', 's_break']
        self.plot_info_clor = ['black', 'yellow', 'green', 'pink', 'purple', 'red', 'blue']

    def resample_callback(self, ds, bars):
        # 数据太少,无法计算均线
        if self.r_high[-1] is None:
            print 'not enough bars for sma, skipped'
            return
        pre_close = self.r_close[-1]
        high = self.r_high[-1]
        low = self.r_low[-1]

        # # --使用http://www.yafco.com/show.php?contentid=261740计算方法--
        # s_setup = high + 0.35*(pre_close-low)
        # self.s_enter = (1.07/2)*(high+low)-0.07*low
        # self.b_enter = (1.07/2)*(high+low)-0.07*high
        # b_setup = pre_close - 0.35*(high - pre_close)
        # self.b_break = s_setup+0.2*(s_setup-b_setup)
        # self.s_break = b_setup-0.25*(s_setup-b_setup)
        # #  --使用http://www.yafco.com/show.php?contentid=261740计算方法 end --

        # --使用Pivot Points计算方法--
        pivot_point = (high + low + pre_close) / 3
        self.b_break = high + self.break_factor * (pivot_point - low)
        self.s_setup = pivot_point + high - low
        self.s_enter = pivot_point + self.rev_factor * (pivot_point - low)
        self.b_enter = pivot_point - self.rev_factor * (high - pivot_point)
        self.b_setup = pivot_point - (high - low)
        self.s_break = low - self.break_factor * (high - pivot_point)
        #  --使用Pivot Points计算方法 end --
        self.plot_info[0].append(pivot_point)
        self.plot_info[1].append(self.b_break)
        self.plot_info[2].append(self.s_setup)
        self.plot_info[3].append(self.s_enter)
        self.plot_info[4].append(self.b_enter)
        self.plot_info[5].append(self.b_setup)
        self.plot_info[6].append(self.s_break)
        self.candy_info[0].append(self.r_open_ds[-1])
        self.candy_info[1].append(self.r_high_ds[-1])
        self.candy_info[2].append(self.r_low_ds[-1])
        self.candy_info[3].append(self.r_close_ds[-1])
        self.candy_info[4].append(self.getCurrentDateTime())

    def on_bars(self, bars):
        if len(self.r_close) < 1 or self.b_break == -1:
            return
        # 获取所有仓位
        positions = list(self.getActivePositions())
        if len(positions) > 1:
            return
        elif len(positions) ==1 and positions[0].exitActive():
            return
            # raise Exception('we should at most have one position in this strategy.')
        self.buy_top_point = max(self.o_close_ds[-1], self.buy_top_point)
        self.sell_low_point = min(self.o_close_ds[-1], self.sell_low_point)
        trade_type = self.gen_trade_signal(bars)
        if trade_type == self.TRADE_TYPE.BUY:
            if len(positions) == 0:
                # self.print_status(self.o_close_ds[-2], self.o_close_ds[-1],bars.getDateTime())
                self.buy_top_point = self.o_close_ds[-1]
                self.enterLong(self.instrument, 1, True)
            else:
                if positions[0].getShares() < 0:
                    # self.print_status(self.o_close_ds[-2], self.o_close_ds[-1],bars.getDateTime())
                    positions[0].exitMarket()
                    self.buy_top_point = self.o_close_ds[-1]
                    self.enterLong(self.instrument, 1, True)
        elif trade_type == self.TRADE_TYPE.SELL:
            if len(positions) == 0:
                # self.print_status(self.o_close_ds[-2],self.o_close_ds[-1],bars.getDateTime())
                self.sell_low_point = self.o_close_ds[-1]
                self.enterShort(self.instrument, 1, True)
            else:
                if positions[0].getShares() > 0:
                    # self.print_status(self.o_close_ds[-2], self.o_close_ds[-1],bars.getDateTime())
                    positions[0].exitMarket()
                    self.sell_low_point = self.o_close_ds[-1]
                    self.enterShort(self.instrument, 1, True)
        elif trade_type == self.TRADE_TYPE.STOP:
            if positions[0].getShares() != 0:
                # self.print_status(self.o_close_ds[-2], self.o_close_ds[-1], bars.getDateTime())
                positions[0].exitMarket()

    def print_status(self, pre_close, cur_close, ds):
        print 'dateTime:', ds, 'pre_close:', pre_close, 'cur_close:', cur_close
        print 'b_break:', self.b_break, 's_enter:', self.s_enter, 'b_enter:', self.b_enter, 's_break:', self.s_break

    def gen_trade_signal(self, bars):
        # if len(self.o_close_ds) <= 2 or self.o_close_ds[-2] is None:
        if len(self.r_close) < 1:
            # print 'not enough bars for sma, skipped'
            return self.TRADE_TYPE.NAN
        pre_close = self.o_close_ds[-2]
        pre_status = -1
        if pre_close > self.s_enter:
            pre_status = 1
        elif pre_close < self.b_setup:
            pre_status = 2
        else:
            pre_status = 0
        # self.plot_info[7].append(pre_status)
        # 获取所有仓位
        positions = list(self.getActivePositions())
        if len(positions) > 1:
            return self.TRADE_TYPE.NAN
            # raise Exception('we should at most have one position in this strategy.')
        cur_close = bars[self.instrument].getClose()

        # 价格突破上限
        if cur_close > self.b_break:
            return self.TRADE_TYPE.BUY

        # 价格突破下线
        if cur_close < self.s_break:
            return self.TRADE_TYPE.SELL

        # 价格由高落入波段 做空阶段
        if cur_close < self.s_enter and self.pre_status == 1:
            return self.TRADE_TYPE.SELL

        # 价格由低落入波段 做多阶段
        if cur_close > self.b_enter and self.pre_status == 2:
            return self.TRADE_TYPE.BUY

        # 判断是否止盈止损
        positions = list(self.getActivePositions())
        if len(positions) == 1:
            if positions[0].getShares() < 0:
                if cur_close < self.buy_top_point - self.stop_point:
                    return self.TRADE_TYPE.STOP
            elif positions[0].getShares() > 0:
                if cur_close > self.sell_low_point + self.stop_point:
                    return self.TRADE_TYPE.STOP
            # return self.TRADE_TYPE.NAN
        return self.TRADE_TYPE.NAN

    @classmethod
    def get_log_key(cls, params):
        return '-'.join(str(params[key]) for key in sorted(params.keys()))

    # 策略开始
    def on_start(self):
        # print 'start cash:', self.getBroker().getCash()
        return

    # 策略结束
    def on_finish(self, bars):
        # self.plot_signal(bar_name)
        # print 'end cash:', self.getBroker().getCash()
        return

    # 开仓成功
    def on_enter_ok(self, position):
        entry_order = position.getEntryOrder()  # 该仓位的开仓orde
        output = '\t'.join(
            str(i) for i in ('enter', position.getInstrument(), position.getShares(), entry_order.getAvgFillPrice()))
        # self.info(output)

    # 开仓失败
    def on_enter_canceled(self, position):
        print 'enter canceled!'

    # 平仓成功
    def on_exit_ok(self, position):
        exit_order = position.getExitOrder()
        output = '\t'.join(
            str(i) for i in ('exit', position.getInstrument(), position.getShares(), exit_order.getAvgFillPrice()))
        # self.info(output)

    # 平仓失败
    def on_exit_canceled(self, position):
        print 'exit caneled!'
        position.exitMarket()  # 重新平仓

    # 订单状态更新
    def on_order_updated(self, order):
        pass

def param_generator():
    result = []
    for rev_factor in range(5, 12, 2):
        for break_factor in range(8, 20, 2):
            for profit_stop_point in (30, 60, 90, 120):
                tmp = dict(
                    window_size=1,
                    # resample_frequency= Frequency.MINUTE * resample_frequency,
                    resample_frequency=Frequency.DAY,
                    profit_stop_point=profit_stop_point,  # 策略参数
                    break_factor=break_factor / 10.0,
                    rev_factor=rev_factor / 10.0,
                )
                result.append(tmp)
    return result


def test_sql(instrument, strategyClass):
        import multiprocessing
        from myalgotrade.feed import Frequency
        from myalgotrade.util import dbutil
        from datetime import datetime
        from myalgotrade.feed import feed_manager
        from myalgotrade.optimizer import run_optimizer, jobutil
        import pprint
        _start_time = datetime.now()
        print 'start time', _start_time
        ranges = {
            # '2010-x': ([datetime(2010, 1, 1), datetime(2010, 7, 1)], [datetime(2010, 7, 1), datetime(2011, 1, 1)]),
            # '2011-s': ([datetime(2010, 7, 1), datetime(2011, 1, 1)], [datetime(2011, 1, 1), datetime(2011, 7, 1)]),
            # '2011-x': ([datetime(2011, 1, 1), datetime(2011, 7, 1)], [datetime(2011, 7, 1), datetime(2012, 1, 1)]),
            '2012-s': ([datetime(2011, 7, 1), datetime(2012, 1, 1)], [datetime(2012, 1, 1), datetime(2012, 7, 1)]),
            '2012-x': ([datetime(2012, 1, 1), datetime(2012, 7, 1)], [datetime(2012, 7, 1), datetime(2013, 1, 1)]),
            '2013-s': ([datetime(2012, 7, 1), datetime(2013, 1, 1)], [datetime(2013, 1, 1), datetime(2013, 7, 1)]),
            '2013-x': ([datetime(2013, 1, 1), datetime(2013, 7, 1)], [datetime(2013, 7, 1), datetime(2014, 1, 1)]),
            '2014-s': ([datetime(2013, 7, 1), datetime(2014, 1, 1)], [datetime(2014, 1, 1), datetime(2014, 7, 1)]),
            '2014-x': ([datetime(2014, 1, 1), datetime(2014, 7, 1)], [datetime(2014, 7, 1), datetime(2015, 1, 1)]),
            '2015-s': ([datetime(2014, 7, 1), datetime(2015, 1, 1)], [datetime(2015, 1, 1), datetime(2015, 7, 1)]),
            '2015-x': ([datetime(2015, 1, 1), datetime(2015, 7, 1)], [datetime(2015, 7, 1), datetime(2016, 1, 1)]),
        }
        start_date = datetime(2011, 7, 1)
        end_date = datetime(2016, 1, 1)
        feed_infos = dbutil.get_dominant_contract_infos(instrument, Frequency.MINUTE*5, start_date, end_date, 7)
        feed_mng = feed_manager.SqlserverFeedManager(feed_infos)

        pprint.pprint(feed_infos)
        # strategy_class = RBreaker
        # param_generator_factory = param_generator
        log_key = 'Optimizer-' + '-' + instrument

        # func_get_feeds_by_range = feed_mng.get_feeds_by_range
        results, combined_result = run_optimizer(feed_mng.get_feeds_by_range, strategyClass, param_generator,
                                                 ranges,
                                                 log_key, jobutil.Comparator(), port=50002,
                                                 batch_size=1)
        result = combined_result.analyze_result
        print '\ncombined result:'
        result.show_result()

        _end_time = datetime.now()
        print 'end time', _end_time
        print 'time used', _end_time - _start_time
        processes = []
        processes.append(multiprocessing.Process(target=result.plotEquityCurve, args=(log_key,)))

        for name in sorted(results.keys()):
            result = results[name]
            print
            print 'range: ', name
            print 'params: ', result[0].getParameters()
            print 'train result:', result[0].getResult().analyze_result
            print 'test result:', result[1]
            print 'analyze result:'
            result[1].analyze_result.show_result()
            # processes.append(multiprocessing.Process(target=result[1].analyze_result.plotEquityCurve,
            #                                          args=('-'.join(str(i) for i in (instrument, name, result[0].getParameters())),)))

        for process in processes:
            process.start()
            #
            # for process in processes:
            #     process.join()

if __name__ == '__main__':
    # '['SR', 'L', 'P', 'M', 'RB', 'RU']:
    # ['RB', 'RM','RU]:
    for instrument in ['RB']:
        test_sql(instrument, RBreaker)

# def run_sample_sql(experiment_key, strategy_class, instrument, param, start, end, frequency, before_days=0):
#     # 获取该品种的主力合约时间段
#     feed_infos = dbutil.get_dominant_contract_infos(instrument, frequency, start, end, before_days)
#     print 'feed infos:'
#     pprint.pprint(feed_infos)
#     feed_mng = feed_manager.DataServerFeedManager(feed_infos)  # feed管理器
#     feeds_dict = feed_mng.get_feeds_by_range(start, end)  # 获取feed
#     print 'feeds:'
#     pprint.pprint(feeds_dict)
#     # log key 用来标识每次回测的log文件，这里采用 experiment_key + instrument
#     log_key = strategy.log_path_delimiter.join((experiment_key, instrument))
#     result = strategy.run_strategy(strategy_class, feeds_dict, log_key, param, initial_cash=1000000,
#                                    use_previous_cash=False)
#     # process = multiprocessing.Process(target=result.analyze_result.plotEquityCurve, args=(log_key,))
#     # process.start()  # notebook中无法开多进程，在其他ide中跑
#     return result, log_key
#
#
# if __name__ == '__main__':
#     args = dict(
#         experiment_key='RBreaker',  # log标识符
#         strategy_class=RBreaker,  # 回测的策略类
#         param={'window_size': 1,
#                'resample_frequency': Frequency.DAY,
#                'profit_stop_point': 20,
#                'break_factor':1.5,
#                'rev_factor':1,},  # 策略参数
#         start=datetime(2015, 1, 1),  # 开始时间
#         end=datetime(2016, 1, 1),  # 结束时间
#         frequency=Frequency.MINUTE*5 ,  # 输入bar的频率
#         before_days=0,  # 成为主力合约前多少天开始取数据
#     )
#
#     all_instruments = tradeutil.all_commodity_set
#     result, log_key = run_sample_sql(instrument='rb', **args)
