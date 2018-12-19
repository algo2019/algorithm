import datetime

from Common.Command import Command
from TradeEngine.GlobleConf import MonitorServerConf


class HeartBeatsCommand(Command):
    def __init__(self, monitor_server):
        self.__monitor_server = monitor_server
        super(HeartBeatsCommand, self).__init__(name='CheckHeartBeatsCommand')

    def execute(self):
        now = datetime.datetime.now()
        for name in self.__monitor_server.heart_beats:
            if now - self.__monitor_server.heart_beats[name] >= datetime.timedelta(seconds=MonitorServerConf.heart_beat_timeout):
                self.__monitor_server.states[name] = 'HeartBeatTimeOut'
            else:
                self.__monitor_server.states[name] = 'HeartBeatOK'
