import os
from myalgotrade import dataServerFeed
import cPickle as pickle
from myalgotrade import context
import json
import importlib
from pyalgotrade.barfeed import OptimizerBarFeed
from myalgotrade.mapreduce import FeedForPickle
import myalgotrade

path_myalgotrade = myalgotrade.__file__
shell_folder = path_myalgotrade[:path_myalgotrade.rfind('/')]
shell_path = os.path.join(shell_folder, 'mapreduce', 'submmit.sh')


def run_task(strategy_class, feed_dict, param_set, log_key, hadoop_path,
             hdfs_path, **kwargs):
    log_path = os.path.join(context.log_root, 'mr-' + log_key)
    if not os.path.isdir(log_path):
        os.mkdir(log_path)

    feed_path = gen_feed_file(feed_dict, log_path)
    param_path, param_dict = gen_param_file(param_set, log_path)
    config_path, class_path = gen_config_file(strategy_class, log_path)

    result_path = os.path.join(log_path, 'output.txt')

    ret = os.system('sh %s %s %s %s %s %s %s %s %s' %
                    (shell_path, hadoop_path, class_path, config_path, param_path, feed_path, result_path,
                     hdfs_path, log_key))

    results = get_result(result_path)
    ret = {}
    for pid in param_dict:
        ret[pid] = {
            'param': param_dict[pid],
            'result': results[pid]
        }
    return ret


def get_result(result_path):
    results = {}
    with open(result_path, 'r') as f:
        for line in f:
            term = line.strip().split()
            pid = int(term[0])
            result = term[1]
            results[pid] = result
    return results


def gen_feed_file(feed_dict, log_path):
    path = os.path.join(log_path, 'feeds_pickle.txt')
    with open(path, 'w') as f:
        pickle.dump(len(feed_dict), f)
        for key in feed_dict:
            pickle.dump(key, f)
            feed_dict[key].pickle_dump(f)
    return path


def gen_param_file(param_list, log_path):
    count = 0
    param_dict = {}
    for param in param_list:
        param_dict[count] = param
        count += 1
    print 'total params:', count
    path = os.path.join(log_path, 'params.txt')
    output = '\n'.join(
        str(i) + '\t' + ';'.join(str(key) + ':' + str(value) for key, value in param_dict[i].items())
        for i in sorted(param_dict.keys())
    )
    with open(path, 'w') as f:
        f.write(output)
    return path, param_dict


def gen_config_file(strategy_class, log_path):
    module_name = strategy_class.__module__
    class_name = strategy_class.__name__
    module = importlib.import_module(module_name)
    class_path = module.__file__
    if class_path[-1] == 'c':
        class_path = class_path[:-1]

    conf = {}
    conf['module'] = module_name.split('.')[-1]
    conf['name'] = class_name
    config_path = os.path.join(log_path, 'conf.txt')
    with open(config_path, 'w') as f:
        json.dump(conf, f)

    return config_path, class_path


def gen_feed_dict(feed_for_pickle):
    feeds = {}

    feed_dict = {}
    for name in feed_for_pickle.bars_dict.keys():
        feed_dict[name] = OptimizerBarFeed(feed_for_pickle.frequency_dict[name], feed_for_pickle.instruments_dict[name],
                                           feed_for_pickle.bars_dict[name])
    return feed_dict


def sample_param_generator():
    for ma_long in range(40, 200, 100):
        for ma_short in range(2, 40, 10):
            yield {
                'ma_long': ma_long,
                'ma_short': ma_short,
            }


def test(strategy_class, feed_dict, param_list, log_key):
    from myalgotrade import strategy
    import datetime
    start_time = datetime.datetime.now()
    feed_for_pickle = FeedForPickle(feed_dict)
    count = 0
    for param in param_list:
        feeds = gen_feed_dict(feed_for_pickle)
        result = strategy.run_strategy(strategy_class, feeds, log_key, param, initial_cash=1000000)
        print '\t'.join(str(i) for i in ('reduce', count, result.analyze_result.getSharpeRatio()))
        count += 1

    end_time = datetime.datetime.now()
    print 'start time', start_time
    print 'end time', end_time
    print 'time used:', end_time - start_time
    exit(0)


def main():
    import pprint
    feed_dict = {
        'L1505': dataServerFeed.dataServerFeed('L1505', '20150101', '20150401', '1m'),
        'L1509': dataServerFeed.dataServerFeed('L1509', '20150501', '20150701', '1m')
    }

    from myalgotrade.strategy import sample
    strategy_class = sample.SampleStrategy
    log_key = "jnq-test"
    user = 'dtest'
    # test(strategy_class, feed_dict, param_generator(), log_key)

    hadoop_path = '/data1/ug_coin/backtest/jnq'
    hdfs_path = '/user/ug_coin/nianqiang.jing/'
    results = run_task(strategy_class, feed_dict, sample_param_generator(), log_key, hadoop_path, hdfs_path)

    print 'results:'
    pprint.pprint(results)

    print 'done'
    pass


if __name__ == '__main__':
    main()
