from Common.Command import IntervalCommand, Command
from TradeEngine.GlobleConf import StartConf
from TradeEngine.GlobleConf import Sys
from TradeEngine.GlobleConf import SysWidget
from TradeEngine.TradeClient.AutoSaveOpr import State
import psutil
from TradeEngine.MonitorClient import Monitor
import socket
import datetime


MemoryWarnPercentage = 5
DiskWarnPercentage = 5
CupWarnPercentage = 1
Interval = 10


class ServerMonitor(Command):
    def __init__(self):
        super(ServerMonitor, self).__init__(name='ServerMonitor')
        self._state = State(StartConf.PublishKey, Sys.ServerApp, self.name)
        self._ip = socket.gethostbyname(socket.gethostname())
        self._state.set_state('last_check_time', None)

    def check_memory(self):
        mem = psutil.virtual_memory()
        percentage = (mem.available + 0.0) / mem.total * 100
        if percentage <= MemoryWarnPercentage:
            Monitor.get_server_log(self.name).ERR(msg='Memory Avilable is {:.2f}%'.format(percentage))
        return percentage

    def check_disk(self):
        disk = psutil.disk_usage('.')
        percentage = (disk.free + 0.0) / disk.total * 100
        if percentage <= DiskWarnPercentage:
            Monitor.get_server_log(self.name).ERR(msg='Disk Free is {:.2f}%'.format(percentage))
        return percentage

    def check_cpu(self):
        cpu = psutil.cpu_times()
        percentage = cpu.idle / sum(cpu) * 100
        if percentage <= CupWarnPercentage:
            Monitor.get_server_log(self.name).ERR(msg='Cup Idle is {:.2f}%'.format(percentage))
        return percentage

    def execute(self):
        mem = self.check_memory()
        disk = self.check_disk()
        idle = self.check_cpu()

        self._state.set_state('last_check_time', str(datetime.datetime.now())[:19])
        self._state.set_state('info', 'ip:{} mem:{:.2f}% disk:{:.2f}% cpu:{:.2f}%'.format(self._ip, mem, disk, idle))


class IntervalCheckServerCommand(IntervalCommand):
    def __init__(self):
        super(IntervalCheckServerCommand, self).__init__(Interval, ServerMonitor(), SysWidget.get_external_engine())
