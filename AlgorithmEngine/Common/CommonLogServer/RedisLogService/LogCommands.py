# -*- coding: utf-8 -*-
"""
LogCommands.py
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import datetime
import json

from Common.Command import Command
from Common.PubSubAdapter.RedisPubSub import RedisPubSub
from Common.CommonLogServer import Conf


class LogCommand(Command):
    def __init__(self, pk, log_name, name, level, source, msg, args):
        super(LogCommand, self).__init__(name=log_name)
        self.level = level
        self.source = source
        self.msg = msg
        self.tags = 0x0
        self.key = Conf.get_key(pk, name)
        self.dt = str(datetime.datetime.now())
        if len(args):
            self.msg = self.msg % args

    @property
    def publish_msg(self):
        return json.dumps({
            'datetime': self.dt,
            'level': self.level,
            'source': self.source,
            'msg': self.msg,
            'tags': self.tags
        })

    @property
    def show_msg(self):
        return '[{}] [{}] [{}]'.format(self.dt, self.source, self.msg)


class LocalLogCommand(LogCommand):
    def __init__(self, pk, log_name, name, level, source, msg, args):
        super(LocalLogCommand, self).__init__(pk, log_name, name, level, source, msg, args)

    def execute(self):
        print self.key, self.show_msg


class PublishLogCommand(LogCommand):
    __REDIS = None

    @classmethod
    def redis(cls):
        if PublishLogCommand.__REDIS is None:
            PublishLogCommand.__REDIS = RedisPubSub(Conf.REDIS_HOST, Conf.REDIS_PORT)
        return PublishLogCommand.__REDIS

    def __new__(cls, *args, **kwargs):
        if Conf.DEBUG:
            rtn = object.__new__(LocalLogCommand)
            rtn.__init__(*list(args), **kwargs)
            return rtn
        return object.__new__(cls)

    def __init__(self, pk, log_name, name, level, source, msg, args):
        super(PublishLogCommand, self).__init__(pk, log_name, name, level, source, msg, args)

    def execute(self):
        try:
            self.redis().publish(self.key, self.publish_msg)
        except:
            self.redis().publish(self.key, json.dumps({
                'datetime': self.dt,
                'level': 'ERR',
                'source': self.name,
                'msg': str(self.level) + str(self.source) + str(self.msg),
            }))


class ServiceLogger(object):
    """
    RedisServiceLogger
    """

    def __init__(self, system, source, log_name, default_name):
        # type: (str, str, str, str) -> None
        self._pk = system
        self._log_name = log_name
        self._source = source
        self._name = default_name

    def publish(self, name, level, msg, *args):
        # type: (str, str, str, tuple) -> None
        PublishLogCommand(self._pk, self._log_name, name or self._name, level, self._source, msg, args).execute()

    def DEBUG(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.publish(name, 'DEBUG', msg, *args)

    def debug(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.DEBUG(name, msg, *args)

    def INFO(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.publish(name, 'INFO', msg, *args)

    def info(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.INFO(name, msg, *args)

    def ERR(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.publish(name, 'ERR', msg, *args)

    def error(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.ERR(name, msg, *args)

    def WARN(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.publish(name, 'WARN', msg, *args)

    def warn(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.WARN(name, msg, *args)

    def warnning(self, name=None, msg='', *args):
        # type: (str, str, tuple) -> None
        self.WARN(name, msg, *args)


class Logger(object):
    """
    RedisLogger
    """

    def __init__(self, system, name, source, log_name):
        # type: (str, str, str) -> None
        self._pk = system
        self._log_name = log_name
        self._name = name
        self._source = source

    def publish(self, level, msg, *args):
        # type: (str, str, tuple) -> None
        PublishLogCommand(self._pk, self._log_name, self._name, level, self._source, msg, args).execute()

    def DEBUG(self, msg, *args):
        # type: (str, tuple) -> None
        self.publish('DEBUG', msg, *args)

    def debug(self, msg, *args):
        # type: (str, tuple) -> None
        self.DEBUG(msg, *args)

    def INFO(self, msg, *args):
        # type: (str, tuple) -> None
        self.publish('INFO', msg, *args)

    def info(self, msg, *args):
        # type: (str, tuple) -> None
        self.INFO(msg, *args)

    def ERR(self, msg, *args):
        # type: (str, tuple) -> None
        self.publish('ERR', msg, *args)

    def error(self, msg, *args):
        # type: (str, tuple) -> None
        self.ERR(msg, *args)

    def WARN(self, msg, *args):
        # type: (str, tuple) -> None
        self.publish('WARN', msg, *args)

    def warn(self, msg, *args):
        # type: (str, tuple) -> None
        self.WARN(msg, *args)

    def warnning(self, msg, *args):
        # type: (str, tuple) -> None
        self.WARN(msg, *args)
