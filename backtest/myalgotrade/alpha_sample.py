#!/usr/bin/env python
from myalgotrade.strategy import sample
from myalgotrade.strategy import Frequency
from myalgotrade.broker import tradeutil


def func_default_param(instrument):
    return {
        'SR': {
            'ma_short': 5,
            'ma_long': 20
        },
        'L': {
            'ma_short': 3,
            'ma_long': 25,
        },
    }[instrument]


def func_param_select(instrument):
    def select_param(results):
        best_sharpe = -100
        for pid, content in results.items():
            result = dict([(kv[0], float(kv[1])) for kv in [p.split(':') for p in content['result'].split(';')]])
            if result['sharpe'] > best_sharpe:
                best_sharpe = result['sharpe']
                best_id = pid
        return results[best_id]['param']

    return select_param


def func_param_generate(instrument):
    def _param_generator_factory():
        for ma_short in range(1, 15, 2):
            for ma_long in range(min(ma_short * 2, 20), 60, 5):
                yield {
                    'ma_short': ma_short,
                    'ma_long': ma_long,
                }

    return _param_generator_factory


ALPHA = {
    'name': 'alpha0',
    'strategy_class': sample.SampleStrategy,
    'frequency': Frequency.MINUTE * 5,
    'train_param': True,
    'train_window': 200,
    'test_window': 150,
    'func_param_generate': func_param_generate,
    'func_param_select': func_param_select,
    'func_default_param': func_default_param,

    'instruments': {
        'SR': {
            'lots': 1,
            'train_param': False,
        },
        'L': {
            'lots': 2,
        }
    }
}


from myalgotrade.util import alpha_runner
import pprint
import cPickle as Pickle
import json
if __name__ == '__main__':
    result = alpha_runner.run_alpha(alpha=ALPHA)
    pprint.pprint(result)
