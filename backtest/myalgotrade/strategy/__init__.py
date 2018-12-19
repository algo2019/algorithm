import os
import datetime

import pyalgotrade.strategy
from pyalgotrade.broker import Order

from myalgotrade import broker
from myalgotrade import resultAnalyzer
from myalgotrade.broker import tradeutil
from myalgotrade.context import log_root
from myalgotrade.feed import Frequency
from myalgotrade.dataServerFeed.OnLineSysBar import Bar

import pandas as pd
import pprint

log_path_delimiter = '_'
trade_log_suffix = '.txt'
day_summary_log_suffix = log_path_delimiter + 'day-summary' + '.txt'
data_log_suffix = log_path_delimiter + 'data-log.csv'


def combine_result(results, log_name, factor=None):
    log_path = os.path.join(log_root, log_name)
    if factor is None:
        factor = {}
    ret = StrategyRecord(
        trade_log=log_path + trade_log_suffix,
        day_summary_log=log_path + day_summary_log_suffix,
        sub_records=results,
    )
    resultAnalyzer.combine_log(results, ret.trade_log, factor)
    resultAnalyzer.combine_summary(results, ret.day_summary_log, factor)
    ret.analyze()
    return ret


def run_strategy(strategy_class, feed_dict, log_key, params, initial_cash=None, use_previous_cash=False):
    print
    print 'running strategy:', strategy_class.__module__ + '.' + strategy_class.__name__
    print 'params:', params
    print 'feeds:', sorted(feed_dict.keys())
    results = {}
    param_log_key = strategy_class.get_log_key(params)
    cash = initial_cash
    for bar_name in sorted(feed_dict.keys()):
        # print
        # print 'feed:', bar_name, 'cash:', cash
        bar_feed = feed_dict[bar_name]
        log_name = log_path_delimiter.join((log_key, strategy_class.__name__, bar_name, param_log_key))
        log_path = os.path.join(log_root, log_name)
        strat = strategy_class(bar_feed, log_path, params, cash)
        strat.run()
        result = strat.get_strategy_record()
        result.analyze()
        results[bar_name] = result
        if use_previous_cash:
            cash = strat.getBroker().getEquity()
            if cash <= 0:
                print 'lose all cash, stop running following feeds'
                break
        else:
            cash = initial_cash
    combined_log_key = log_path_delimiter.join((log_key, param_log_key))
    combined_result = combine_result(results, combined_log_key)

    # print
    # print 'run strategy result:',
    # pprint.pprint(combined_result)
    # print 'result analyze:'
    # combined_result.analyze_result.show_result()
    return combined_result


class StrategyRecord(dict):
    def __init__(self, trade_log, day_summary_log, data_log=None, analyze_result=None, sub_records=None):
        super(StrategyRecord, self).__init__(trade_log=trade_log, day_summary_log=day_summary_log,
                                             data_log=data_log,
                                             analyze_result=analyze_result)
        self['sub_records'] = {}
        if sub_records is not None:
            self['sub_records'].update(sub_records)

    def analyze(self):
        self.analyze_result = resultAnalyzer.resultAnalyzer(self.trade_log, self.day_summary_log)

    @classmethod
    def construct_by_log_name(cls, log_name):
        trade_log = os.path.join(log_root, log_name + trade_log_suffix)
        day_summary_log = os.path.join(log_root, log_name + day_summary_log_suffix)
        return cls(trade_log, day_summary_log)

    @property
    def data_log(self):
        return self['data_log']

    @property
    def trade_log(self):
        return self['trade_log']

    @property
    def day_summary_log(self):
        return self['day_summary_log']

    @property
    def analyze_result(self):
        return self['analyze_result']

    @analyze_result.setter
    def analyze_result(self, result):
        self['analyze_result'] = result

    @property
    def sub_records(self):
        return self['sub_records']

    def show_result(self):
        if self.analyze_result is not None:
            self.analyze_result.show_result()


class StrategyBase(pyalgotrade.strategy.BacktestingStrategy):
    """base class for backtesting strategy. subclass should not override methods start with '_'
    or named in CamelCase (eg. onStart, onBars). override those methods named like on_xxx(eg. on_start, on_bars).

    """
    datetime_format_day = '%Y-%m-%d'
    datetime_format_datetime = '%Y-%m-%d %H:%M:%S'
    log_delimiter = '\t'

    default_initial_cash = 10000000

    action_str = {
        Order.Action.BUY: 'buy',
        Order.Action.SELL: 'sell',
        Order.Action.BUY_TO_COVER: 'buy_cover',
        Order.Action.SELL_SHORT: 'sell_short'
    }

    @classmethod
    def get_log_key(cls, params):
        raise Exception('should override to get log name.')

    @classmethod
    def get_mapper_output(cls, result):
        analyzer = result.analyze_result
        output = {
            'sharpe': analyzer.getSharpeRatio(),
            'trades': analyzer.getAllCount(),
            'profit': analyzer.getNetProfit(),
            'fund': analyzer.getMaxFundUse(),
            'drawdown': analyzer.getMaxDrawDown()[0],
            'return': analyzer.getAnnualizedReturn()[0],
            'return_risk_ratio': analyzer.getReturnRiskRatio(),
            'win_ratio': analyzer.getWinRatio(),
            'profit_loss_ratio': analyzer.getProfitLossRatio()
        }
        ret = ';'.join(str(key) + ':' + str(value) for key, value in output.items())
        return ret

    def __init__(self, bar_feed, log_path, params, cash_or_brk=None, ouput_log=True):
        """

        :param bar_feed:
        :param log_path:
        :param params:
        :param cash_or_brk:
        :return:
        """
        if cash_or_brk is None:
            cash_or_brk = self.default_initial_cash
        if not isinstance(cash_or_brk, broker.Broker):
            cash_or_brk = broker.Broker(cash_or_brk, bar_feed)
            cash_or_brk.setAllowNegativeCash(True)
            # cash_or_brk.setAllowNegativeCash(False)
            cash_or_brk.setCommission(tradeutil.BasicCommission())

        super(StrategyBase, self).__init__(bar_feed, cash_or_brk=cash_or_brk)
        self._params = params
        self._log_path = log_path
        self._trade_log_file = open(log_path + trade_log_suffix, 'w')
        self._day_summary_file_path = log_path + day_summary_log_suffix
        self._day_summary_file = open(self._day_summary_file_path, 'w')
        self._day_summary_file_name = self._day_summary_file.name
        self._day_summary_file.close()
        self._output_log = ouput_log
        self._data_log_name = None
        if self._output_log:
            self._data_log_name = log_path + data_log_suffix
        self._strategy_record = StrategyRecord(
            trade_log=self._trade_log_file.name,
            day_summary_log=self._day_summary_file_name,
            data_log=self._data_log_name,
        )
        self._last_day_equity = self.getBroker().getEquity()
        # self.resampleBarFeed(Frequency.DAY, self._summary_day)
        self._logs = {}
        self._day_summary = {}
        self._trade_log = []

    def log_data(self, name, value):
        if not self._output_log:
            return
        if self._logs.get(name) is None:
            self._logs[name] = {}
        self._logs[name][self.getCurrentDateTime()] = str(value)

    def _summary_day(self, dt, bars):
        # print 'day summary:', dt, bars.keys()
        equity = self.getBroker().getEquity()
        day_profit = equity - self._last_day_equity
        self._last_day_equity = equity
        key = dt.strftime(self.datetime_format_day)
        self._day_summary[key] = self._day_summary.get(key, 0.0) + day_profit

    def get_strategy_record(self):
        return self._strategy_record

    def getResult(self):
        raise Exception('use get_strategy_record method instead')

    # subclass should not override following methods.
    def onStart(self):
        self.on_start()

    def onFinish(self, bars):
        # exit active positions on finish bar.
        for position in set(self.getActivePositions()):
            if not position.exitActive():
                position.exitMarket(True)
        self.getBroker().onBars(bars.getDateTime(), bars)
        if len(self.getActivePositions()) > 0:
            for position in self.getActivePositions():
                print position.getInstrument(), position.getShares()
            raise Exception('position not exit after barfeed finish.')
        self._summary_day(bars.getDateTime(), bars)

        # output day summary
        s = pd.Series(self._day_summary)
        s.to_csv(self._day_summary_file_path, sep=self.log_delimiter)
        # output trade log
        print >> self._trade_log_file, '\n'.join(i for i in self._trade_log)
        super(StrategyBase, self).onFinish(bars)

        # output log datas.
        if self._output_log:
            df = pd.DataFrame(dict((name, pd.Series(self._logs[name], name=name)) for name in self._logs))
            # print 'log data path:',  self._data_log_name
            df.to_csv(self._data_log_name, index_label='datetime')

        self.on_finish(bars)

        self._trade_log_file.close()

        self.getBroker().getOrderUpdatedEvent().unsubscribe(self._BaseStrategy__onOrderEvent)
        self._BaseStrategy__barFeed.getNewValuesEvent().unsubscribe(self._BaseStrategy__onBars)
        self.getDispatcher().getStartEvent().unsubscribe(self.onStart)
        self.getDispatcher().getIdleEvent().unsubscribe(self._BaseStrategy__onIdle)

        del self.getBroker()._Broker__barFeed
        del self.getDispatcher()._Dispatcher__subjects
        del self._BaseStrategy__barFeed

        # print 'barfeed finished.', 'cash:', self.getBroker().getEquity()

    def onBars(self, bars):
        if bars.getDateTime().time() == datetime.time(15, 0, 0):
            self._summary_day(bars.getDateTime(), bars)
        self.on_bars(bars)

    def _record_trade_log(self, order):
        execution_info = order.getExecutionInfo()
        order_price = execution_info.getPrice()
        action = self.action_str[order.getAction()]
        execute_time = execution_info.getDateTime()
        submmit_time = order.getSubmitDateTime()
        trade_log = self.log_delimiter.join(str(i) for i in (
            submmit_time.strftime(self.datetime_format_datetime),
            action,
            order.getInstrument(),
            order_price,
            order.getQuantity(),
        ))
        # print trade_log
        self._trade_log.append(trade_log)

    def onEnterOk(self, position):
        order = position.getEntryOrder()
        self._record_trade_log(order)
        self.on_enter_ok(position)

    def onEnterCanceled(self, position):
        self.on_enter_canceled(position)

    def onExitOk(self, position):
        order = position.getExitOrder()
        self._record_trade_log(order)
        self.on_exit_ok(position)

    def onExitCanceled(self, position):
        self.on_exit_canceled(position)

    def onIdle(self):
        raise Exception('backtesing should not call this idle function.')

    def onOrderUpdated(self, order):
        self.on_order_updated(order)

    # subclass should override following methods to execute strategy.
    def on_start(self):
        pass

    def on_finish(self, bars):
        pass

    def on_bars(self, bars):
        raise NotImplementedError()

    def on_enter_ok(self, position):
        pass

    def on_enter_canceled(self, position):
        pass

    def on_exit_ok(self, position):
        pass

    def on_exit_canceled(self, position):
        pass

    def on_order_updated(self, order):
        pass
