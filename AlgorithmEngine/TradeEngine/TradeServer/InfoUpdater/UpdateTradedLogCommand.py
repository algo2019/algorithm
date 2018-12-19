import datetime

from TradeEngine.GlobleConf import SysEvents
from TradeEngine.GlobleConf import SysWidget, StartConf
from Common.Command import Command
from TradeEngine.MonitorClient import Monitor
import traceback


class UpdateTradedLogCommand(Command):
    def __init__(self, order):
        super(UpdateTradedLogCommand, self).__init__(name='UpdateSharesCommand')
        self.__order = order

    def execute(self):
        try:
            SysWidget.get_trade_log_dao().put_trade(StartConf.PublishKey, self.__order.strategy_name,
                                                    datetime.datetime.now(), self.__order.instrument,
                                                    self.__order.offset, self.__order.trade_side,
                                                    self.__order.volume, self.__order.filled_volume,
                                                    self.__order.filled_price)
            msg = '%s#%s#%s#%s#%d#%d#%2.2f' % (
                str(datetime.datetime.now())[:19], self.__order.instrument, self.__order.offset,
                self.__order.trade_side, self.__order.volume, self.__order.filled_volume, self.__order.filled_price)
            SysWidget.get_logger('UpdateTradedLogCommand', self.__order.strategy_name).TRADE(msg)
            Monitor.get_server_log(self.name).INFO(self.__order.strategy_name, 'trade update:%s', msg)
        except:
            Monitor.get_server_log(self.name).ERR(self.__order.strategy_name, traceback.format_exc())


def traded_log(order):
    SysWidget.get_log_engine().add_command(UpdateTradedLogCommand(order))


def start_command():
    SysEvents.OrderOver.subscribe(traded_log)
