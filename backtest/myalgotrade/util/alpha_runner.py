
import datetime
import pprint

from myalgotrade.util import dbutil
from myalgotrade.feed import feed_manager
from myalgotrade import strategy
from myalgotrade.mapreduce import optimizer
from myalgotrade.broker import tradeutil
from myalgotrade.dataServerFeed.DomBarFeed import BarFeed


def run_fix_param(config, start_date, end_date):
    instrument = config['instrument']
    frequency = config['frequency']
    strategy_class = config['strategy_class']
    experiment_key = config['name']
    func_default_param = config['func_default_param']
    param = func_default_param(instrument)

    before_days = config['before_days']
    after_days = config['after_days']
    feed = BarFeed(instrument, start_date, end_date, frequency, before_days, after_days)
    feed_dict = {instrument: feed}

    # feed_info = dbutil.get_dominant_contract_infos(instrument, frequency, start_date, end_date, before_days)
    # feed_mng = feed_manager.DataServerFeedManager(feed_info)
    # feed_dict = feed_mng.get_feeds_by_range(start_date, end_date)
    log_key = strategy.log_path_delimiter.join((experiment_key, instrument))
    result = strategy.run_strategy(strategy_class, feed_dict, log_key, param)
    return result


datetime_format = '%Y%m%d'


def generate_train_test_ranges(instrument, train_window, test_window, start_date, end_date):
    one_day = datetime.timedelta(days=1)

    train_start = start_date - train_window
    available_start = tradeutil.get_available_start(instrument)
    if train_start < available_start:
        train_start = available_start
    test_start = train_start + train_window

    ranges = {}
    while test_start < end_date:
        train_start = test_start - train_window
        train_end = test_start - one_day
        test_end = test_start + test_window
        if test_end > end_date:
            test_end = end_date
        range_name = test_start.strftime(datetime_format) + '-' + test_end.strftime(datetime_format)
        ranges[range_name] = ((train_start, train_end), (test_start, test_end))
        test_start = test_end + one_day
    return ranges


def run_train_param(config, start_date, end_date):
    instrument = config['instrument']
    frequency = config['frequency']
    strategy_class = config['strategy_class']
    experiment_key = config['name']
    before_days = config.get('before_days', 0)
    after_days = config.get('after_days', 0)

    train_window = datetime.timedelta(days=config['train_window'])
    test_window = datetime.timedelta(days=config['test_window'])
    ranges = generate_train_test_ranges(instrument, train_window, test_window, start_date, end_date)
    pprint.pprint(ranges)

    feed_infos = dbutil.get_dominant_contract_infos(instrument, frequency, start_date - train_window, end_date,
                                                    before_days=before_days, after_days=after_days)
    feed_mng = feed_manager.DataServerFeedManager(feed_infos)

    pprint.pprint(feed_infos)

    log_key = strategy.log_path_delimiter.join((experiment_key, instrument))

    func_get_feeds_by_range = feed_mng.get_feeds_by_range
    params_generator_factory = config['func_param_generate'](instrument)
    func_param_select = config['func_param_select'](instrument)
    hadoop_path = '/data1/ug_coin/backtest/jnq'
    hdfs_path = '/user/ug_coin/nianqiang.jing'

    results, combined_result = optimizer.run_optimizer(func_get_feeds_by_range=feed_mng.get_feeds_by_range,
                                                       strategy_class=strategy_class,
                                                       params_generator_factory=params_generator_factory,
                                                       named_ranges=ranges,
                                                       func_select_param=func_param_select,
                                                       log_key=log_key,
                                                       hadoop_path=hadoop_path,
                                                       hdfs_path=hdfs_path,
                                                       show_plot=False,
                                                       )
    result = combined_result
    return result


default_start_date = datetime.datetime(2015, 1, 1)
default_end_date = datetime.datetime(2016, 1, 1)


def run_alpha(alpha, start_date=default_start_date, end_date=default_end_date):
    configs = {}
    default_config = dict([(k, v) for k, v in alpha.items() if k != 'instruments'])
    for instrument, config in alpha['instruments'].items():
        configs[instrument] = dict(**default_config)
        configs[instrument].update(config)
        configs[instrument]['instrument'] = instrument

    experiment_key = alpha['name']
    results = {}
    for instrument, config in configs.items():
        available_start = tradeutil.get_available_start(instrument)
        tmp_start_date = start_date
        if tmp_start_date < available_start:
            tmp_start_date = available_start
        train_param = config['train_param']
        print instrument
        if not train_param:
            result = run_fix_param(config, tmp_start_date, end_date)
        else:
            result = run_train_param(config, tmp_start_date, end_date)
        results[instrument] = result
        print 'result:',
        pprint.pprint(result)
        result.show_result()
        print

    combine_result = strategy.combine_result(results, experiment_key)
    return combine_result
