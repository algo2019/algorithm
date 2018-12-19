import datetime

from Common.Command import Command, IntervalCommand
from TradeEngine.GlobleConf import SysWidget, Sys, StartConf
import time
from TradeEngine.MonitorClient import Monitor
from TradeEngine.TradeClient.AutoSaveOpr import State


class CheckActiveOrderCommand(Command):
    TIMEOUT = 10
    NOTIFIED_INTERVAL = 60 * 10

    def __init__(self):
        super(CheckActiveOrderCommand, self).__init__(name='CheckActiveOrder')
        self._cache = {}
        self._notified_order = {}
        self._state = State(StartConf.PublishKey, Sys.ServerApp, self.name)
        self._state.set_state('last_check_time', None)

    def execute(self):
        SysWidget.get_active_order_list().handler(self._check_active_order)
        self._state.set_state('last_check_time', str(datetime.datetime.now())[:19])

    def _check_active_order(self, orders):
        temp = {}
        temp_notified = {}
        for order in orders:
            temp[order.order_ref] = (time.time(), order)

        for key in self._cache:
            last = temp.get(key)
            if last is not None and last[0] - self._cache[key][0] >= self.TIMEOUT:
                if key not in self._notified_order or time.time() - self._notified_order[key] > self.NOTIFIED_INTERVAL:
                    Monitor.get_server_log(self.name).ERR(last[1].strategy_name, 'active order {} timeout!'.format(key))
                    temp_notified[key] = time.time()
                else:
                    temp_notified[key] = self._notified_order[key]

        self._cache = temp
        self._notified_order = temp_notified
        self._state.set_state('info', 'count:{}'.format(len(orders)))


class IntervalCheckActiveOrderCommand(IntervalCommand):
    def __init__(self):
        super(IntervalCheckActiveOrderCommand, self).__init__(CheckActiveOrderCommand.TIMEOUT,
                                                              CheckActiveOrderCommand(),
                                                              SysWidget.get_external_engine())
