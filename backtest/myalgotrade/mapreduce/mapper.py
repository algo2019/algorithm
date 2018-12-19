#!/usr/bin/env python

import sys
import os

path_old_packages = '/usr/lib64/python2.6/site-packages'
path_packages = './packages'
path_mylib = './mylib'

path_config = os.path.join(path_mylib, 'conf.txt')
path_feed = os.path.join(path_mylib, 'feeds_pickle.txt')


if path_old_packages in sys.path:
    sys.path.remove(path_old_packages)
sys.path.append(path_packages)
sys.path.append(path_mylib)

# path_temp = '/data1/ug_coin/nianqiang.jing/packages'
# sys.path.append(path_temp)

import json
import cPickle as pickle
import importlib

from myalgotrade.strategy import run_strategy


def gen_feed_dict(_path_feed=None):
    from myalgotrade.dataServerFeed.DomBarFeed import BarFeed
    feed_dict = {}
    if _path_feed is None:
        _path_feed = path_feed
    with open(_path_feed, 'r') as f:
        for _ in xrange(pickle.load(f)):
            key = pickle.load(f)
            feed_dict[key] = BarFeed.pickle_load(f)
    return feed_dict


def get_strategy_class():
    f = open(path_config, 'r')
    conf = json.load(f)
    f.close()

    module_name = conf['module']
    class_name = conf['name']
    module = importlib.import_module(module_name)
    strategy_class = getattr(module, class_name)
    return strategy_class


def get_param(param_str):
    return dict((p[0], p[1]) for p in [kv.split(':') for kv in param_str.split(';')])


def reset_feed_dict(feed_dict):
    for k, v in feed_dict.iteritems():
        v.reset()

log_key = 'result'


def main():
    feed_dict = gen_feed_dict()
    strategy_class = get_strategy_class()
    for line in sys.stdin:
        term = line.strip().split()
        pid = term[0]
        param = get_param(term[1])
        result = run_strategy(strategy_class, feed_dict, log_key, param)
        print 'reduce', '\t', pid, '\t', strategy_class.get_mapper_output(result)
        reset_feed_dict(feed_dict)

if __name__ == '__main__':
    main()