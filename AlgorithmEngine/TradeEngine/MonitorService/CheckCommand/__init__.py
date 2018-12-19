from Common.Command import IntervalCommand
from TradeEngine.GlobleConf import MonitorServerConf
from TradeEngine.GlobleConf import Sys
from TradeEngine.GlobleConf import SysWidget
from TradeEngine.TradeClient.AutoSaveOpr import State
from HeartBeatsCommand import HeartBeatsCommand
from DrawDownCommand import DrawDownCommand
from RemotePositionCommand import IntervalRemotePositionCommand
from CheckActiveOrderCommand import IntervalCheckActiveOrderCommand
from ServerMonitor import IntervalCheckServerCommand


def start_check_commands(monitor_server):
    SysWidget.get_redis_reader().delete(State.get_key(Sys.ServerApp, '*'))

    print 'check command:starting heartbeat check command'
    IntervalCommand(MonitorServerConf.heart_beat_check_period, HeartBeatsCommand(monitor_server), SysWidget.get_external_engine())
    print 'check command:starting remote position check command'
    IntervalRemotePositionCommand()
    print 'check command:starting active order check command'
    IntervalCheckActiveOrderCommand()
    print 'check command:starting server check command'
    IntervalCheckServerCommand()
