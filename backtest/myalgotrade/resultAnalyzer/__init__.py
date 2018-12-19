from __future__ import division
import pandas as pd


def combine_log(results, combined_log_path, factors=None):
    if factors is None:
        factors = {}

    sep = '\t'

    names_trade = ['datetime', 'action', 'instrument', 'price', 'lots']
    sort_value = {
        'sell': 0,
        'buy_cover': 1,
        'sell_short': 2,
        'buy': 3,
    }
    trade_dfs = []

    for key, result in results.items():
        path = result.trade_log
        df = pd.read_csv(path, sep=sep, names=names_trade, parse_dates=['datetime'])
        factor = int(factors.get(key, 1))
        df.lots = df.lots * factor
        trade_dfs.append(df)
    df_trade = pd.DataFrame(columns=names_trade)
    if len(trade_dfs) > 0:
        df_trade = pd.concat(trade_dfs, axis=0)
        df_trade['sort_value'] = df_trade['action'].apply(lambda x: sort_value[x])
        df_trade = df_trade.sort_values(by=['datetime', 'sort_value'], axis=0)
    df_trade.to_csv(path_or_buf=combined_log_path, columns=names_trade, index=False, header=False, sep=sep)


def combine_summary(results, combined_summary_path, factors=None):
    if factors is None:
        factors = {}
    names_day = ['date', 'profit']
    sep = '\t'
    day_dfs = []

    for key, result in results.items():
        path = result.day_summary_log
        df = pd.read_csv(path, sep=sep, names=names_day, parse_dates=['date'], index_col='date')
        factor = int(factors.get(key, 1))
        df.profit = df.profit * factor
        day_dfs.append(df)
    df_day = pd.DataFrame(columns=['all'])
    if len(day_dfs) > 0:
        df_day = pd.concat(day_dfs, axis=1).fillna(0)
        df_day['all'] = df_day.apply(sum, axis=1)
    df_day.to_csv(path_or_buf=combined_summary_path, columns=['all'], index=True, header=False, sep=sep)


from calc import calcProfit
from calc import calcDrawDownAndSharpeRatio
import datetime
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass



class resultAnalyzer(object):
    def __init__(self, log_path, summary_path):
        self._log_path = log_path
        self._summary_path = summary_path

        self._all_count = 0
        self._net_profit = 0
        self._win_ratio = 0
        self._profit_loss_ratio = 0
        self._max_drawdown = 0
        self._longest_drawdown_duration = datetime.timedelta()
        self._max_fund_use = 0
        self._annualized_return = 0
        self._compound_annualized_return = 0
        self._sharpe_ratio = 0
        self._annualized_return_rate = 0
        self._return_risk_ratio = 0
        self._compound_annualized_return_rate = 0

        self.calc()

    def calc(self):
        [self._all_count, self._net_profit, self._win_ratio, self._profit_loss_ratio, max_margin] = calcProfit(
            self._log_path)
        [self._max_drawdown, self._longest_drawdown_duration, self._sharpe_ratio,
         years_traded] = calcDrawDownAndSharpeRatio(self._summary_path)
        self._max_fund_use = max_margin# + self._max_drawdown
        self._annualized_return = (self.getNetProfit() / years_traded) if years_traded >0 else 0
        if self._max_fund_use > 0:
            self._annualized_return_rate = self._annualized_return / self._max_fund_use
            self._return_risk_ratio = self._annualized_return / self._max_drawdown if self._max_drawdown > 0 else 0
            self._compound_annualized_return_rate = pow(self.getNetProfit() / self._max_fund_use + 1, 1 / years_traded) - 1

    def getAllCount(self):
        return self._all_count

    def getNetProfit(self):
        return self._net_profit

    def getWinRatio(self):
        return self._win_ratio

    def getProfitLossRatio(self):
        return self._profit_loss_ratio

    def getMaxDrawDown(self):
        return self._max_drawdown, self._max_drawdown / self._max_fund_use if self._max_fund_use > 0 else 0

    def getLongestDrawDownDuration(self):
        return self._longest_drawdown_duration

    def getMaxFundUse(self):
        return self._max_fund_use

    def getAnnualizedReturn(self):
        return self._annualized_return, self._annualized_return_rate, self._compound_annualized_return_rate

    def getReturnRiskRatio(self):
        return self._return_risk_ratio

    def getSharpeRatio(self):
        return self._sharpe_ratio

    def plotEquityCurve(self, label='profit'):
        file_object = open(self._summary_path, 'r')
        lines = file_object.readlines()
        file_object.close()

        equity = [0]
        for line in lines:
            equity.append(float(line.strip().split('\t')[1]) + equity[-1])
        del equity[0]
        plt.plot(equity, label=label)
        plt.legend(loc='upper left')
        plt.show()

    def __repr__(self):
        ret = {
            'all count': self._all_count,
            'net profit': self._net_profit,
            'sharpe ratio': self._sharpe_ratio,
        }
        return str(ret)

    def show_result(self):
        print '\tall count', self.getAllCount()
        print '\tnet profit', self.getNetProfit()
        print '\twin ratio', self.getWinRatio()
        print '\tprofit loss ratio', self.getProfitLossRatio()
        print '\tmax fund use', self.getMaxFundUse()
        print '\tmax drawdown', self.getMaxDrawDown()
        print '\tlongest drawdown duration', self.getLongestDrawDownDuration()
        print '\tannual return', self.getAnnualizedReturn()
        print '\treturn risk ratio', self.getReturnRiskRatio()
        print '\tsharp ratio', self.getSharpeRatio()



def main():
    log_path = 'D:\\backtest_platform\\logs\\signle_run_strat_0.5_3_60_20.txt'
    summary_path = 'D:\\backtest_platform\\logs\\signle_run_strat_0.5_3_60_20_day-summary.txt'
    result = resultAnalyzer(log_path=log_path, summary_path=summary_path)
    print 'all count', result.getAllCount()
    print 'net profit', result.getNetProfit()
    print 'win ratio', result.getWinRatio()
    print 'profit loss ratio', result.getProfitLossRatio()
    print 'max drawdown', result.getMaxDrawDown()
    print 'longest drawdown duration', result.getLongestDrawDownDuration()
    print 'annual return', result.getAnnualizedReturn()
    print 'sharp ratio', result.getSharpeRatio()
    result.plotEquityCurve()


if __name__ == '__main__':
    main()
