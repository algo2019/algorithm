# -*- coding: utf-8 -*-
"""
mlogging.py
"""
from Common.CommonLogServer.RedisLogService.LogCommands import Logger, ServiceLogger
from TradeEngine.GlobleConf import Sys
import StartConf

__all__ = ['MyLogger', 'MyServerLogger']


class MyLogger(Logger):
    """
    MyLogger Base on RedisLogger
    """

    def __init__(self, source, name=None):
        # type: (str) -> None
        super(MyLogger, self).__init__(StartConf.PublishKey, name or Sys.ServerApp, source, source)

    def TRADE(self, msg, *args):
        # type: (str, tuple) -> None
        """
        :param msg:
        :param args:
        """
        self.publish('TRADE', msg, *args)

    def trade(self, msg, *args):
        # type: (str, tuple) -> None
        """
        :param msg:
        :param args:
        """
        self.TRADE(msg, *args)


class MyServerLogger(ServiceLogger):
    """
    ServerLogger
    """
    def __init__(self, source, log_name):
        # type: (str, str) -> None
        super(MyServerLogger, self).__init__(StartConf.PublishKey, source, log_name, Sys.ServerApp)

    def TRADE(self, strategy, msg, *args):
        # type: (str, str, tuple) -> None
        """
        :param strategy:
        :param msg:
        :param args:
        """
        self.publish(strategy, 'TRADE', msg, *args)

    def trade(self,strategy, msg, *args):
        # type: (str, str, tuple) -> None
        """
        :param strategy:
        :param msg:
        :param args:
        """
        self.TRADE(strategy, msg, *args)
