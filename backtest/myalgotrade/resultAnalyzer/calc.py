from __future__ import division
import datetime
from pyalgotrade.utils import stats
import math
from myalgotrade.broker import tradeutil


TRADING_DAYS_ONE_YEAR = 245

def calcProfit(log_path):
    alltrades = []
    profittrades = []
    losstrades = []
    commission = []
    margin = [0]


    file_object = open(log_path)
    lines = file_object.readlines()
    file_object.close()

    position = {}
    commission_object = tradeutil.BasicCommission()

    for line in lines:
        info = line.strip().split('\t')
        instrument = info[2]
        trade_unit = tradeutil.get_trade_unit(instrument)
        margin_ratio = tradeutil.get_margin_ratio(instrument)


        if instrument not in position:
            position[instrument] = {'buy_position': 0, 'sell_position': 0, 'buy_avg_price': 0, 'sell_avg_price': 0}


        transType = info[1]
        price = float(info[3])
        lots = int(float(info[4]))

        if transType == 'buy':
            new_position = position[instrument]['buy_position'] + lots
            if new_position != 0:
                position[instrument]['buy_avg_price'] = (position[instrument]['buy_avg_price'] * position[instrument]['buy_position']
                                                     + price * lots) / new_position
            position[instrument]['buy_position'] = new_position
            margin.append(margin[-1] + price * trade_unit * lots * margin_ratio)

        elif transType == 'sell_short':
            new_position = position[instrument]['sell_position'] + lots
            if new_position != 0:
                position[instrument]['sell_avg_price'] = (position[instrument]['sell_avg_price'] * position[instrument]['sell_position']
                                                      + price * lots) / new_position
            position[instrument]['sell_position'] = new_position
            margin.append(margin[-1] + price * trade_unit * lots * margin_ratio)


        elif transType == 'sell':
            position[instrument]['buy_position'] -= lots
            commission.append(commission_object.calculate_commission(instrument, position[instrument]['buy_avg_price'] + price, lots))
            net_profit = ((price - position[instrument]['buy_avg_price']) * trade_unit * lots) -commission[-1]
            margin.append(margin[-1] - position[instrument]['buy_avg_price'] * trade_unit * lots * margin_ratio)

            if net_profit > 0:
                profittrades.append(net_profit)
            elif net_profit < 0:
                losstrades.append(net_profit)
            alltrades.append(net_profit)

        elif transType == 'buy_cover':
            position[instrument]['sell_position'] -= lots
            commission.append(commission_object.calculate_commission(instrument, position[instrument]['sell_avg_price'] + price, lots))
            net_profit = ((position[instrument]['sell_avg_price'] - price) * trade_unit * lots) - commission[-1]
            margin.append(margin[-1] - position[instrument]['sell_avg_price'] * trade_unit * lots * margin_ratio)

            if net_profit > 0:
                profittrades.append(net_profit)
            elif net_profit < 0:
                losstrades.append(net_profit)
            alltrades.append(net_profit)

    if len(alltrades) == 0:
        return [0, 0, 0, 0, 0]
    trades_count = len(alltrades)
    net_profit = sum(alltrades)
    win_ratio = len(profittrades) / trades_count
    if len(losstrades) == 0:
        profit_loss_ratio = 1
    elif len(profittrades) == 0:
        profit_loss_ratio = 0
    else:
        profit_loss_ratio = sum(profittrades) / len(profittrades) / (abs(sum(losstrades)) / len(losstrades))
    max_margin = max(margin)
    return [trades_count, net_profit, win_ratio, profit_loss_ratio, max_margin]


def calcDrawDownAndSharpeRatio(summary_path):
    file_object = open(summary_path, 'r')
    lines = file_object.readlines()
    file_object.close()

    date = []
    profit = []
    equity = []
    for line in lines:
        date.append(datetime.datetime.strptime(line.strip().split('\t')[0], '%Y-%m-%d').date())
        profit.append(float(line.strip().split('\t')[1]))
        equity.append(sum(profit))

    if len(date) == 0:
        return [0, 0, 0, 0]
    sharpe_ratio = calcSharpeRatio(profit)
    [max_drawdown, longest_drawdown_duration] = calcDrawDown(date, equity)

    years_traded = ((date[-1] - date[0]).days + 1) / 365

    return [max_drawdown, longest_drawdown_duration, sharpe_ratio, years_traded]


def calcSharpeRatio(profit_list):
    sharpe_ratio = 0
    volatility = stats.stddev(profit_list, 1)
    if volatility != 0:
        avg_profit = stats.mean(profit_list)
        sharpe_ratio = float(avg_profit / volatility) * math.sqrt(TRADING_DAYS_ONE_YEAR)
    return sharpe_ratio

def calcDrawDown(date_list, equity_list):
    max_drawdown = 0
    longest_drawdown_duration = datetime.timedelta()

    high_watermark = None
    low_watermark = None
    high_date = None
    last_date = None
    for i in xrange(len(date_list)):
        date = date_list[i]
        equity = equity_list[i]

        last_date = date
        if high_watermark is None or equity >= high_watermark:
            high_watermark = equity
            low_watermark = equity
            high_date = date
        else:
            low_watermark = min(low_watermark, equity)

        longest_drawdown_duration = max(longest_drawdown_duration, last_date - high_date)
        max_drawdown = min(max_drawdown, low_watermark - high_watermark)
    max_drawdown = -max_drawdown
    return [max_drawdown, longest_drawdown_duration]


