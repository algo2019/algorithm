import unittest

import time

from TradeEngine.ServerApp import ServerApp
from TradeEngine.TradeClient.RemoteStrategyCaller import RemoteStrategyCaller
from TradeEngine.GlobleConf import SysWidget, AdjustStateV
from TradeEngine.UnitTest.MockModel import split
from TradeEngine.MonitorClient import Monitor


class ServerAppTest(unittest.TestCase):
    server = None
    remote_caller = None
    max_try = 20
    logger = Monitor.get_logger('ServerAppTest')

    def setUp(self):
        redis_host = '10.4.37.206'
        redis_port = 6379
        trade_host = '10.4.37.206'
        trade_port = 51000
        log_path = '/Users/renren1/test'
        args = (redis_host, redis_port, trade_host, trade_port, log_path)
        if self.server is None:
            self.server = ServerApp(args).start()

        self.strategy_name = 'unittest'
        self.obj_name = 'object'
        self.instruments = ['ag1612', 'MA609']

        if self.remote_caller is None:
            self.remote_caller = RemoteStrategyCaller(self.strategy_name).start()

            # self.set_up_without_network()

    def set_up_without_network(self):
        pass

    def tearDown(self):
        pass

    def test(self):
        split()
        self.logger.INFO('start strategy')
        self.remote_caller.start_strategy(self.obj_name, self.instruments)
        #
        tick_data = SysWidget.get_tick_data()
        for i in range(self.max_try):
            if len(tick_data.instrument_set) != 0:
                break
            time.sleep(0.1)
        self.assertSetEqual(set(self.instruments), tick_data.instrument_set)
        self.logger.INFO('start strategy ok')
        #
        split()
        self.logger.INFO('wait for tick data')
        while tick_data.get(self.instruments[0]) is None:
            time.sleep(0.1)
        split()
        self.logger.INFO('adjust to 4')
        state = self.remote_caller.adjust_to(self.obj_name, self.instruments[0], 4, 3)
        for i in range(self.max_try):
            if state.STATE in AdjustStateV.OverStates:
                break
            time.sleep(0.5)
        self.logger.INFO('adjust state:%s', AdjustStateV.to_string(state.STATE))
        self.assertTrue(state.STATE in AdjustStateV.OverStates)
        self.logger.INFO('adjust to 4 ok')
        split()
        self.logger.INFO('adjust to -4')
        state2 = self.remote_caller.adjust_to(self.obj_name, self.instruments[0], -4, 3)
        for i in range(self.max_try):
            if state2.STATE in AdjustStateV.OverStates:
                break
            time.sleep(0.5)
        self.logger.INFO('adjust state:%s', AdjustStateV.to_string(state.STATE))
        self.assertTrue(state2.STATE in AdjustStateV.OverStates)
        self.logger.INFO('adjust to -4 ok')
        time.sleep(0.1)
