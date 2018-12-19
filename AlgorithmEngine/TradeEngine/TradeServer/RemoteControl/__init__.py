import cPickle as pickle
import time
import traceback

import CallAction
from Common.Command import Command
from TradeEngine.GlobleConf import RedisKey
from TradeEngine.GlobleConf import Sys
from TradeEngine.GlobleConf import SysWidget
from TradeEngine.MonitorClient import Monitor


class RemoteStrategyController(object):
    def __init__(self):
        self.__name = 'RemoteStrategyController'
        self.__logger = Monitor.get_server_log(self.name)
        self.__started = False

    @property
    def name(self):
        return self.__name

    def start(self):
        if not self.__started:
            self.__started = True
            self.__logger.INFO(msg='started')
            SysWidget.get_redis_reader().subscribe(RedisKey.Publish.RemoteStrategy(), self.process)

    def stop(self):
        if self.__started:
            self.__started = False
            self.__logger.INFO(msg='stoped')
            SysWidget.get_redis_reader().unsubscribe(RedisKey.Publish.RemoteStrategy(), self.process)

    def process(self, msg):
        strategy = msg['channel'].split('.')[-1]
        if not Sys.is_active_strategy(strategy):
            raise Exception('unknown strategy : %s' % strategy)
        obj_name, cmd, args, kwargs = pickle.loads(msg['data'])
        try:
            CallAction.get_action(cmd, strategy, obj_name, args, kwargs).execute()
        except:
            self.__logger.ERR(strategy, traceback.format_exc())
