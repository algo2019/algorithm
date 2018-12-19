import time

from Common.Command import Command
from TradeEngine.GlobleConf import StrategyWidget
from TradeEngine.GlobleConf import MonitorServerConf
from TradeEngine.MonitorClient import Monitor


class DrawDownCommand(Command):
    def __init__(self, monitor_server):
        self.__monitor_server = monitor_server
        self.__last_send_err_time = {}
        super(DrawDownCommand, self).__init__(name='CheckDrawDownCommand')

    def __is_heart_beat(self, strategy):
        return self.__monitor_server.get_state(strategy) == 'HeartBeatOK'

    @staticmethod
    def __is_out_of_range(account):
        return account.draw_down_cash >= MonitorServerConf.max_draw_down

    def __send_err(self, strategy, draw_down_cash):
        if time.time() - self.__last_send_err_time.get(strategy, 0) > 60 * 60 * 6 :
            Monitor.get_server_log(self.name).ERR(strategy, 'draw down : %2.2f !', draw_down_cash)
            self.__last_send_err_time[strategy] = time.time()

    def execute(self):
        try:
            for strategy in StrategyWidget.ACCOUNT:
                account = StrategyWidget.get_account_mgr(strategy)
                if self.__is_out_of_range(account) and self.__is_heart_beat(strategy):
                    self.__send_err(strategy, account.draw_down_cash)
        except RuntimeError, e:
            if str(e) != 'dictionary changed size during iteration':
                raise
