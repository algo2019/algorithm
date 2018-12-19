import multiprocessing
import jobutil
import server
import worker
from myalgotrade import strategy


def start_workers(port):
    print 'need manually start worker:'
    print 'port:', port
    pass


def run_optimizer(func_get_feeds_by_range, strategy_class, params_generator_factory, named_ranges, log_key,
                  result_comparator, port, batch_size):
    results = {}
    if port is None:
        port = jobutil.find_port_by_default()
    start_workers(port)

    for name in sorted(named_ranges.keys()):
        range_ = named_ranges[name]
        train_start, train_end = range_[0]
        test_start, test_end = range_[1]
        train_feed_dict = func_get_feeds_by_range(train_start, train_end)
        test_feed_dict = func_get_feeds_by_range(test_start, test_end)
        print 'stage name:', name
        print 'train range:', train_start, train_end
        print 'test range:', test_start, test_end
        print 'train feeds:', sorted(train_feed_dict.keys())
        print 'test feeds:', sorted(test_feed_dict.keys())
        if len(train_feed_dict) == 0 or len(test_feed_dict) == 0:
            if len(train_feed_dict) == 0:
                print 'train feed empty,',
            else:
                print 'test feed empty,',
            print 'skipped stage.'
            continue
        log_key_train = strategy.log_path_delimiter.join((log_key, 'train', name))
        myserver = server.Server('localhost', port, batch_size)
        train_result = myserver.serve(strategy_class=strategy_class,
                                      bar_feed_dict=train_feed_dict,
                                      parameter_set=params_generator_factory(),
                                      log_key=log_key_train,
                                      result_comparator=result_comparator
                                      )
        myserver.server_close()

        log_key_test = strategy.log_path_delimiter.join((log_key, 'test', name))

        print 'train result:'
        train_result.getResult().analyze_result.show_result()
        multiprocessing.Process(target=train_result.getResult().analyze_result.plotEquityCurve,
                                args=(log_key_train + '\n' + str(train_result.getParameters()),)).start()

        test_result = strategy.run_strategy(strategy_class, test_feed_dict, log_key_test, train_result.getParameters())
        multiprocessing.Process(target=test_result.analyze_result.plotEquityCurve, args=(log_key_test,)).start()

        results[name] = (train_result, test_result)

    log_key_combined = strategy.log_path_delimiter.join((log_key, 'all-combined'))
    combined_result = strategy.combine_result({name: v[1] for name, v in results.items()}, log_key_combined)

    return results, combined_result

    # best_result = my_server.run_server_once(feed_mngr, train_start, train_end, param_generator, port=port_dict['ab'])


def test_sql(instrument):
    import multiprocessing
    from myalgotrade.strategy import dt_strategy
    from myalgotrade.feed import Frequency
    from myalgotrade.util import dbutil
    from datetime import datetime
    from myalgotrade.feed import feed_manager
    import pprint
    _start_time = datetime.now()
    print 'start time', _start_time
    ranges = {
        # '2011': ([datetime(2010, 1, 1), datetime(2011, 1, 1)], [datetime(2011, 1, 1), datetime(2012, 1, 1)]),
        '2012': ([datetime(2010, 1, 1), datetime(2012, 1, 1)], [datetime(2012, 1, 1), datetime(2013, 1, 1)]),
        '2013': ([datetime(2011, 1, 1), datetime(2013, 1, 1)], [datetime(2013, 1, 1), datetime(2014, 1, 1)]),
        '2014': ([datetime(2012, 1, 1), datetime(2014, 1, 1)], [datetime(2014, 1, 1), datetime(2015, 1, 1)]),
        '2015': ([datetime(2013, 1, 1), datetime(2015, 1, 1)], [datetime(2015, 1, 1), datetime(2015, 7, 1)]),
    }
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2015, 7, 1)
    # instrument = 'I'
    feed_infos = dbutil.get_dominant_contract_infos(instrument, Frequency.MINUTE, start_date, end_date, 7)
    feed_mng = feed_manager.SqlserverFeedManager(feed_infos)

    pprint.pprint(feed_infos)
    strategy_class = dt_strategy.DTStrategy
    param_generator_factory = dt_strategy.dt_param_generator_factory
    log_key = 'test-optimizer-sql5' +'-' + instrument

    func_get_feeds_by_range = feed_mng.get_feeds_by_range

    results, combined_result = run_optimizer(func_get_feeds_by_range, strategy_class, param_generator_factory, ranges,
                                             log_key, jobutil.Comparator(), port=jobutil.port_dict['dt'],
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


def test_dt():
    from myalgotrade.strategy import dt_strategy
    from myalgotrade import feed
    from myalgotrade.feed import feed_manager
    import multiprocessing

    from datetime import datetime
    ranges = {
        '8': ([datetime(2015, 3, 1), datetime(2015, 5, 1)], [datetime(2015, 5, 1), datetime(2015, 6, 1)]),
        '9': ([datetime(2015, 3, 1), datetime(2015, 6, 1)], [datetime(2015, 6, 1), datetime(2015, 7, 1)]),
        '10': ([datetime(2015, 3, 1), datetime(2015, 7, 1)], [datetime(2015, 7, 1), datetime(2015, 9, 1)]),
    }

    csv_infos = {
        # 'l': ('../data/test_bar.csv', feed.Frequency.MINUTE, feed.RowParser()),
        'l': (
            '../data/l1509_1min.csv', feed.Frequency.MINUTE, feed.GenericRowParser(frequency=feed.Frequency.MINUTE)),

    }
    # fm = SqlDomFeedManager('l', (2015,3,1), (2015,9,1), frequency, frontdays)
    # fm.get_by_range(start, end)
    # fm[instrument] = feed
    strategy_class = dt_strategy.DTStrategy
    param_generator_factory = dt_strategy.dt_param_generator_factory
    log_key = 'test-optimizer'

    feed_mng = feed_manager.CsvFeedManager(csv_infos)
    func_get_feeds_by_range = feed_mng.get_feeds_by_range

    results, combined_result = run_optimizer(func_get_feeds_by_range, strategy_class, param_generator_factory, ranges,
                                             log_key, jobutil.Comparator(), port=jobutil.port_dict['dt'],
                                             batch_size=4)
    result = combined_result.analyze_result
    print 'all count', result.getAllCount()
    print 'net profit', result.getNetProfit()
    print 'win ratio', result.getWinRatio()
    print 'profit loss ratio', result.getProfitLossRatio()
    print 'max drawdown', result.getMaxDrawDown()
    print 'longest drawdown duration', result.getLongestDrawDownDuration()
    print 'annual return', result.getAnnualizedReturn()
    print 'sharp ratio', result.getSharpeRatio()

    processes = []
    processes.append(multiprocessing.Process(target=result.plotEquityCurve))

    for name, result in results.items():
        print 'range: ', name
        print 'params: ', result[0].getParameters()
        print 'train result:', result[0].getResult()
        print 'test result:', result[1]
        processes.append(multiprocessing.Process(target=result[1].analyze_result.plotEquityCurve))

    for process in processes:
        process.start()

    for process in processes:
        process.join()


def test_aberration():
    from datetime import datetime
    from myalgotrade.strategy import Aberration
    from myalgotrade import feed
    from myalgotrade.feed import feed_manager
    ranges = {
        '8': ([datetime(2015, 1, 1), datetime(2015, 5, 1)], [datetime(2015, 5, 1), datetime(2015, 11, 1)]),
        '9': ([datetime(2015, 1, 1), datetime(2015, 6, 1)], [datetime(2015, 6, 1), datetime(2015, 11, 1)]),
        '10': ([datetime(2015, 1, 1), datetime(2015, 7, 1)], [datetime(2015, 7, 1), datetime(2015, 11, 1)]),
    }
    csv_infos = {
        'l1509': (
            '../data/l1509_1min.csv', feed.Frequency.MINUTE, feed.GenericRowParser(frequency=feed.Frequency.MINUTE)),
    }
    strategy_class = Aberration.Aberration
    param_generator_factory = Aberration.param_generator_factory

    feed_mng = feed_manager.CsvFeedManager(csv_infos)
    func_get_feeds_by_range = feed_mng.get_feeds_by_range

    results = run_optimizer(func_get_feeds_by_range, strategy_class, param_generator_factory, ranges,
                            port=server.port_dict['ab'])

    for name, result in results.items():
        print 'range: ', name
        print 'params: ', result[0].getParameters()
        print 'train result:', result[0].getResult()
        print 'test result:', result[1]


def main():
    # test_dt()
    # test_aberration()
    # ['i', 'pp', 'm', 'l', 'p', 'y', 'c', 'j', 'cs', 'jm', 'jd', 'ma', 'sr', 'rm', 'ta', 'cf', 'fg', 'zc', 'rb', 'bu', 'ni', 'ru', 'ag', 'cu', 'zn', 'au', 'al']
    instruments = ['I', 'PP', 'M', 'L', 'P', 'Y', 'C', 'J', 'CS', 'JM', 'JD']
    instruments += ['SR', 'RM', 'TA', 'CF', 'FG']
    instruments += ['RB', 'BU', 'RU', 'AG', 'CU', 'ZN', 'AU', 'AL'] #+['NI']
    instruments = list(set(instruments) - {'M', 'L', 'P', 'SR', 'RM', 'TA', 'RB', 'RU', 'AG', 'AU', 'CU', 'CF'})
    print instruments
    for instrument in instruments:
        test_sql(instrument)


if __name__ == '__main__':
    main()
