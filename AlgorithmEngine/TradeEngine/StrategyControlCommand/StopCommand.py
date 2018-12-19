import cPickle as pickle
from Common.Command import Command
from TradeEngine.GlobleConf import SysWidget
from TradeEngine.GlobleConf.RedisKey import Publish
from TradeEngine.GlobleConf import RemoteStrategy as Rsk


class StopCommand(Command):
    def __init__(self, strategy_name):
        self.__strategy_name = strategy_name
        super(StopCommand, self).__init__('StopCommand.%s' % strategy_name)

    def execute(self):
        key = Publish.RemoteCallBack(self.__strategy_name)
        args = (self.name, Rsk.STOP_STRATEGY, tuple())
        SysWidget.get_redis_reader().publish(key, pickle.dumps(args))