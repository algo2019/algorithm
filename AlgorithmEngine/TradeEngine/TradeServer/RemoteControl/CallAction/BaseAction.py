import cPickle as pickle
from Common.Command import Command
from TradeEngine.GlobleConf import RedisKey
from TradeEngine.GlobleConf import SysWidget
from TradeEngine.MonitorClient import Monitor
from Tables import StrategyTable


class BaseAction(Command):
    _logger = Monitor.get_server_log('RemoteCallAction')
    _strategy_table = StrategyTable.create()

    def __init__(self, strategy, obj_name, args, kwargs):
        self._strategy, self._obj_name, self._args, self._kwargs = strategy, obj_name, args, kwargs
        super(BaseAction, self).__init__(name='RemoteCallAction')

    @staticmethod
    def _return(strategy, obj_name, cmd, _return):
        SysWidget.get_redis_reader().publish(RedisKey.Publish.RemoteCallBack(strategy),
                                             pickle.dumps((obj_name, cmd, _return), 2))
