import datetime
import multiprocessing
import pprint

from myalgotrade import strategy
from myalgotrade.mapreduce.runner import run_task
from pyalgotrade import observer


def reset_feeds(feed_dict):
    for feed in feed_dict.values():
        feed.reset()
        feed._BaseFeed__event = observer.Event()


def run_optimizer(func_get_feeds_by_range, strategy_class, params_generator_factory, named_ranges, log_key,
                  func_select_param, hadoop_path, hdfs_path, show_plot=False, **kwargs):
    results = {}

    for name in sorted(named_ranges.keys()):
        start_time = datetime.datetime.now()
        range_ = named_ranges[name]
        train_start, train_end = range_[0]
        test_start, test_end = range_[1]
        print
        print '*************** train and test ******************'
        print 'stage name:', name
        print 'train range:', train_start, train_end
        print 'test range:', test_start, test_end
        train_feed_dict = func_get_feeds_by_range(train_start, train_end)
        test_feed_dict = func_get_feeds_by_range(test_start, test_end)
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
        run_results = run_task(strategy_class=strategy_class,
                               feed_dict=train_feed_dict,
                               param_set=params_generator_factory(),
                               log_key=log_key_train,
                               hadoop_path=hadoop_path,
                               hdfs_path=hdfs_path,
                               )
        train_param = func_select_param(run_results)
        reset_feeds(train_feed_dict)
        train_result = strategy.run_strategy(strategy_class, train_feed_dict, log_key_train, train_param)

        log_key_test = strategy.log_path_delimiter.join((log_key, 'test', name))

        # multiprocessing.Process(target=test_target).start()
        # multiprocessing.Process(target=test_target, args=(train_result.analyze_result.plotEquityCurve,)).start()

        test_result = strategy.run_strategy(strategy_class, test_feed_dict, log_key_test, train_param)

        print
        print 'select param:', train_param

        print '\ntrain result:', train_result
        train_result.analyze_result.show_result()

        print '\ntest result:', test_result
        test_result.analyze_result.show_result()
        if show_plot:
            multiprocessing.Process(target=train_result.analyze_result.plotEquityCurve,
                                    args=(log_key_train + '\n' + str(train_param),)).start()
            multiprocessing.Process(target=test_result.analyze_result.plotEquityCurve, args=(log_key_test,)).start()

        results[name] = (train_param, train_result, test_result)

        end_time = datetime.datetime.now()
        print 'time used for this range:', end_time - start_time
    pprint.pprint(results)
    log_key_combined = strategy.log_path_delimiter.join((log_key, 'all-combined'))
    combined_result = strategy.combine_result(dict((name, v[2]) for name, v in results.items()), log_key_combined)

    return results, combined_result
