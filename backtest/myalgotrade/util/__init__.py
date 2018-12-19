import multiprocessing

def show_analyze_result_process(result):
    process = multiprocessing.Process(target=__show_analyze_result, args=(result,))
    process.start()
    return process


def __show_analyze_result(result):
    print 'all count', result.getAllCount()
    print 'net profit', result.getNetProfit()
    print 'win ratio', result.getWinRatio()
    print 'profit loss ratio', result.getProfitLossRatio()
    print 'max drawdown', result.getMaxDrawDown()
    print 'longest drawdown duration', result.getLongestDrawDownDuration()
    print 'annual return', result.getAnnualizedReturn()
    print 'sharp ratio', result.getSharpeRatio()
    result.plotEquityCurve()


def get_symbol_by_insrument(instrument):
    instrument = str(instrument)
    symbol = ''.join(str.lower(i) for i in instrument if str.isalpha(i))
    return symbol
