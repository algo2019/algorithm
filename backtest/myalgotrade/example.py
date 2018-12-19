from myalgotrade.feed import feed_manager


def example_optimize_dt():
    from strategy import dt_strategy
    from datetime import datetime
    import optimizer
    import feed
    from feed import feed_manager
    from optimizer import server
    ranges = {
        '8': ([datetime(2015, 7, 1), datetime(2015, 8, 1)], [datetime(2015, 8, 1), datetime(2015, 9, 1)]),
        '9': ([datetime(2015, 7, 1), datetime(2015, 9, 1)], [datetime(2015, 9, 1), datetime(2015, 10, 1)]),
        '10': ([datetime(2015, 7, 1), datetime(2015, 10, 1)], [datetime(2015, 10, 1), datetime(2015, 11, 1)]),
    }
    csv_infos = {
        'test1': ('data/test_bar.csv', feed.Frequency.MINUTE, feed.RowParser()),
    }
    strategy_class = dt_strategy.DTStrategy
    param_generator_factory = dt_strategy.dt_param_generator_factory

    feed_mng = feed_manager.CsvFeedManager(csv_infos)
    func_get_feeds_by_range = feed_mng.get_feeds_by_range

    results = optimizer.run_optimizer(func_get_feeds_by_range, strategy_class, param_generator_factory, ranges)
    for name, result in results.items():
        print 'range: ', name
        print 'params: ', result[0].getParameters()
        print 'train result:', result[0].getResult()
        print 'test result:', result[1]

def mapper():
    import sys
    import importlib

    feeds = {}
    for line in sys.stdin:
        term = line.strip().split()
        param = {}
        pid = int(term[0])
        for kv in term[1].split(','):
            k, v = kv.split(':')
            param[k] = v
        for kv in term[2].split(','):
            feed_name, path = kv.split(':')
            if feeds.get(feed_name) is None:
                pass
    raise NotImplementedError('to be implemented.')




def example_run_strategy_dt():
    import strategy
    from strategy import dt_strategy
    from datetime import datetime
    import feed
    import pprint
    # get_feeds_by_date_range = feed_manager.func_single_feed_getter('test1', 'data/test_bar.csv', feed.Frequency.MINUTE,
    #                                                                feed.RowParser())
    csv_infos = {
        'l': ('data/test_bar.csv', feed.Frequency.MINUTE, feed.RowParser()),
        'ag': ('data/test_bar.csv', feed.Frequency.MINUTE, feed.RowParser()),
    }

    strategy_class = dt_strategy.DTStrategy

    param = {
        'k': 5,
        'm': 3,
        'trailing_start': 40,
        'stop_loss_set': 15,
        'adjust': 0,
        'min_point': 1,
        'lots': 1
    }

    feed_mng = feed_manager.CsvFeedManager(csv_infos)
    feeds = feed_mng.get_feeds_by_range(datetime(1900, 1, 1), datetime.now())
    result = strategy.run_strategy(strategy_class, feeds, 'signle_run_strat', param)

    print 'combined result:'
    pprint.pprint(result)


def example_dt():
    print 'run strategy dt'
    example_run_strategy_dt()

    print 'run optimize dt'
    example_optimize_dt()


def example_optimize_ab():
    from strategy import Aberration
    from datetime import datetime
    import optimizer
    from optimizer import server
    import feed
    from feed import feed_manager
    ranges = {
        '8': ([datetime(2015, 1, 1), datetime(2015, 5, 1)], [datetime(2015, 5, 1), datetime(2015, 10, 1)]),
        '9': ([datetime(2015, 1, 1), datetime(2015, 6, 1)], [datetime(2015, 6, 1), datetime(2015, 10, 1)]),
        '10': ([datetime(2015, 1, 1), datetime(2015, 7, 1)], [datetime(2015, 7, 1), datetime(2015, 11, 1)]),
    }
    csv_infos = {
        'l1509': ('data/l1509_1min.csv', feed.Frequency.MINUTE, feed.GenericRowParser(frequency=feed.Frequency.MINUTE)),
    }
    strategy_class = Aberration.Aberration
    param_generator_factory = Aberration.param_generator_factory

    feed_mng = feed_manager.CsvFeedManager(csv_infos)
    func_get_feeds_by_range = feed_mng.get_feeds_by_range

    results = optimizer.run_optimizer(func_get_feeds_by_range, strategy_class, param_generator_factory, ranges)
    for name, result in results.items():
        print 'range: ', name
        print 'params: ', result[0].getParameters()
        print 'train result:', result[0].getResult()
        print 'test result:', result[1]


def example_run_strategy_ab():
    import strategy
    from strategy import Aberration
    from datetime import datetime
    import feed

    csv_infos = {
        'l': ('data/l1509_1min.csv', feed.Frequency.MINUTE, feed.GenericRowParser(frequency=feed.Frequency.MINUTE)),
    }

    strategy_class = Aberration.Aberration

    params = {'boll_period': 50, 'num_std_dev': 3}

    feed_mng = feed_manager.CsvFeedManager(csv_infos)
    feeds = feed_mng.get_feeds_by_range(datetime(1900, 1, 1), datetime.now())
    log_key = 'kkkkkkk'
    strategy.run_strategy(strategy_class, feeds, log_key, params)


def example_ab():
    print 'run strategy ab'
    example_run_strategy_ab()

    print 'run optimize ab'
    example_optimize_ab()


def example_sql_dt(instrument):
    from datetime import datetime
    from myalgotrade.util import dbutil
    from myalgotrade.feed import Frequency
    from myalgotrade import strategy
    from strategy import dt_strategy
    import pprint

    start_date = datetime(2012, 1, 1)
    end_date = datetime(2015, 7, 1)
    #instrument = 'I'
    feed_infos = dbutil.get_dominant_contract_infos(instrument, Frequency.MINUTE*10, start_date, end_date, 4)
    print 'feed infos:'
    pprint.pprint(feed_infos)

    experiment_key = 'example-sql-dt-12'
    feed_mng = feed_manager.SqlserverFeedManager(feed_infos)
    param = {
        'k': 5,
        'm': 3,
        'trailing_start': 60,
        'stop_loss_set': 20,
        'adjust': 0,
    }
    feeds_dict = feed_mng.get_feeds_by_range(start_date, end_date)
    print 'feeds:'
    pprint.pprint(feeds_dict)

    strategy_class = dt_strategy.DTStrategy
    log_key = strategy.log_path_delimiter.join((experiment_key, instrument, strategy_class.get_log_key(param)))
    result = strategy.run_strategy(strategy_class, feeds_dict, log_key, param, initial_cash=1000000, use_previous_cash=True)
    return result, log_key





def select_param(results):
    import pprint
    pprint.pprint(results)
    best_sharpe = -100
    for pid, content in results.items():
        result = dict([(kv[0], float(kv[1])) for kv in [p.split(':') for p in content['result'].split(';')]])
        if result['sharpe'] > best_sharpe:
            best_sharpe = result['sharpe']
            best_id = pid
    return results[best_id]['param']


def example_optimizer(instrument, strategyClass, param_generator_factory, hadoop_path, hdfs_path):
    import multiprocessing
    from myalgotrade.feed import Frequency
    from myalgotrade.util import dbutil
    from datetime import datetime
    from myalgotrade.feed import feed_manager
    import pprint
    from myalgotrade.mapreduce import optimizer

    _start_time = datetime.now()
    print 'start time', _start_time
    ranges = {
        # '2010-x': ([datetime(2010, 1, 1), datetime(2010, 7, 1)], [datetime(2010, 7, 1), datetime(2011, 1, 1)]),
        # '2011-s': ([datetime(2010, 7, 1), datetime(2011, 1, 1)], [datetime(2011, 1, 1), datetime(2011, 7, 1)]),
        # '2011-x': ([datetime(2011, 1, 1), datetime(2011, 7, 1)], [datetime(2011, 7, 1), datetime(2012, 1, 1)]),
        # '2012-s': ([datetime(2011, 7, 1), datetime(2012, 1, 1)], [datetime(2012, 1, 1), datetime(2012, 7, 1)]),
        # '2012-x': ([datetime(2012, 1, 1), datetime(2012, 7, 1)], [datetime(2012, 7, 1), datetime(2013, 1, 1)]),
        # '2013-s': ([datetime(2012, 7, 1), datetime(2013, 1, 1)], [datetime(2013, 1, 1), datetime(2013, 7, 1)]),
        # '2013-x': ([datetime(2013, 1, 1), datetime(2013, 7, 1)], [datetime(2013, 7, 1), datetime(2014, 1, 1)]),
        # '2014-s': ([datetime(2013, 7, 1), datetime(2014, 1, 1)], [datetime(2014, 1, 1), datetime(2014, 7, 1)]),
        # '2014-x': ([datetime(2014, 1, 1), datetime(2014, 7, 1)], [datetime(2014, 7, 1), datetime(2015, 1, 1)]),
        '2015-s': ([datetime(2014, 7, 1), datetime(2015, 1, 1)], [datetime(2015, 1, 1), datetime(2015, 7, 1)]),
        '2015-x': ([datetime(2015, 1, 1), datetime(2015, 7, 1)], [datetime(2015, 7, 1), datetime(2016, 1, 1)]),
    }
    start_date = datetime(2010, 7, 1)
    end_date = datetime(2016, 1, 1)
    feed_infos = dbutil.get_dominant_contract_infos(instrument, Frequency.MINUTE*5, start_date, end_date, 7)
    feed_mng = feed_manager.DataServerFeedManager(feed_infos)

    pprint.pprint(feed_infos)
    # strategy_class = RBreaker

    log_key = 'MR_Optimizer' + '-' + instrument

    # func_get_feeds_by_range = feed_mng.get_feeds_by_range
    results, combined_result = optimizer.run_optimizer(func_get_feeds_by_range=feed_mng.get_feeds_by_range,
                                                       strategy_class=strategyClass,
                                                       params_generator_factory=param_generator_factory,
                                                       named_ranges=ranges,
                                                       func_select_param=select_param,
                                                       log_key=log_key,
                                                       hadoop_path=hadoop_path,
                                                       hdfs_path=hdfs_path,
                                                       show_plot=False,
                                                       )
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
        print 'params: ', result[0]
        print 'train result:', result[1].analyze_result
        print 'test result:', result[2]
        print 'analyze result:'
        result[2].analyze_result.show_result()
        # processes.append(multiprocessing.Process(target=result[1].analyze_result.plotEquityCurve,
        #                                          args=('-'.join(str(i) for i in (instrument, name, result[0].getParameters())),)))

    for process in processes:
        process.start()
        #
        # for process in processes:
        #     process.join()







def main():
    # example_dt()
    # example_ab()
    # example_run_strategy_dt()
    from broker import tradeutil
    import multiprocessing
    process_list = []
    for instrument in tradeutil.all_commodity_set:
        result, log_key = example_sql_dt(str.upper(instrument))
        print log_key
        result = result.analyze_result
        process = multiprocessing.Process(target=result.plotEquityCurve, args=(log_key,))
        process.start()

if __name__ == '__main__':
    # main()
    from myalgotrade.strategy import rbreaker
    hadoop_path = '/data1/ug_coin/backtest/test'
    hdfs_path = '/user/ug_coin/nianqiang.jing'
    example_optimizer('L', rbreaker.RBreaker, rbreaker.param_generator, hadoop_path, hdfs_path)