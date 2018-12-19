import unittest

import time

import datetime

from TradeEngine.TradeClient.BaseStrategy import BaseStrategy
from TradeEngine.CoreEngine import CoreEngine
from TradeEngine.GlobleConf import AdjustStateV
from TradeEngine.UnitTest.MockModel.TickData import TickData
from TradeEngine.GlobleConf import SysWidget

class BaseStrategyTest(unittest.TestCase):
    def setUp(self):
        redis_host = '10.4.37.206'
        redis_port = 6379
        strategy_file = '../TradeClient/BaseStrategy.py'
        self.strategy_name = 'BaseStrategy'
        self.instrument = 'l1609'
        self.name = 'l'
        self.configs = {
            self.name: {
                'instruments': [(self.instrument, '01')],
                'param': {
                    'profit_stop_factor': 0.3,
                    'break_factor': 1.6,
                    'rev_factor': 0.7,
                    'stop_window_size': 3,
                }
            },
        }
        self.tick_data = TickData()
        SysWidget.TICK_DATA = self.tick_data
        self.max_try = 10
        conf = {'RedisHost': redis_host, 'RedisPort': redis_port, 'StrategyFile': strategy_file,
                'StrategyName': self.strategy_name, 'configs': self.configs}
        ce = CoreEngine(conf)
        self.base_strategy = ce.start_engine(BaseStrategy)[0]

    def tearDown(self):
        SysWidget.TICK_DATA = None

    def test(self):
        self.assertEqual(self.base_strategy.name, self.name)
        self.assertEqual(self.base_strategy.strategy_name, self.strategy_name)
        self.assertDictEqual(self.configs[self.name]['param'], self.base_strategy.param)
        #
        self.base_strategy.set_states('time', str(datetime.datetime.now()))
        self.base_strategy.set_state_dict({'state1': '1', 'state2': '2'})
        states = {'k1':'ms', 'k2':'ks'}
        self.base_strategy.set_state_dict(states)
        #
        state = self.base_strategy.adjust_to(self.instrument, 0)
        for i in range(self.max_try):
            if state.STATE in AdjustStateV.OverStates:
                break
            time.sleep(0.1)
        self.assertEqual(self.base_strategy.get_shares_volume(self.instrument, '0'), 0)
        #
        state = self.base_strategy.adjust_to(self.instrument, 4)
        for i in range(self.max_try):
            if state.STATE in AdjustStateV.OverStates:
                break
            time.sleep(0.1)
        self.assertTrue(state.STATE in AdjustStateV.OverStates)
        self.assertEqual(self.base_strategy.get_shares_volume(self.instrument, '0'), 4)
