# -*- coding:utf-8 -*-
import datetime

import CheckCommand
import MonitorMsg
from ServerEngine import Engine
from TradeEngine.GlobleConf import RedisKey
from TradeEngine.GlobleConf import SysWidget, SysEvents


class MonitorService(object):
    def __init__(self):
        self.__key = RedisKey.Publish.HeartBeat('*')
        self.heart_beats = {}
        self.states = {}

    def get_heart_beat(self, name):
        return self.heart_beats.get(name)

    def set_heart_beat(self, name):
        self.heart_beats[name] = datetime.datetime.now()

    def get_state(self, name):
        return self.states.get(name, 'NoHeartBeat')

    def start(self):
        print 'monitor server:starting log process thread'
        SysWidget.get_redis_reader().subscribe(self.__key, SysEvents.MonitorMsgEvent.emit)
        SysEvents.MonitorMsgEvent.subscribe(self.__on_process)
        CheckCommand.start_check_commands(self)
        print 'monitor server:started'

    def __on_process(self, data):
        Engine.add_command(MonitorMsg.get_msg(self, data))
