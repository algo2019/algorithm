# -*- coding:utf-8 -*-

import LogMsg
from Common.RedisClient import RedisClient
from ServerEngine import Engine
from Common.CommonLogServer import Conf


class LogService(object):
    def __init__(self):
        self.__key = Conf.get_key('*', '*')
        self.__err_sender = None
        self.__redis = RedisClient(Conf.REDIS_HOST, Conf.REDIS_PORT, Conf.REDIS_DB)

    @property
    def redis(self):
        return self.__redis

    @property
    def err_sender(self):
        return self.__err_sender

    def start(self):
        print 'file logger server:starting log process thread'
        self.__redis.subscribe(self.__key, self.__on_process)
        print 'file logger server:started'

    def __on_process(self, data):
        Engine.add_command(LogMsg.get_msg(self, data))


if __name__ == '__main__':
    import time
    LogService().start()
    while 1:
        time.sleep(1)
