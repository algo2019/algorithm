import datetime

from Common.Command import AtDateTimeCommand
from Common.Command import Command
from TradeEngine.GlobleConf import StartConf
from TradeEngine.GlobleConf import StrategyWidget, Shares, MonitorServerConf
from TradeEngine.GlobleConf import Sys
from TradeEngine.MonitorClient import Monitor
from TradeEngine.RemoteInfoCommand.GetRemotePositionCommand import GetRemotePositionCommand
from TradeEngine.TradeClient.AutoSaveOpr import State


class RemotePositionCommand(Command):
    def __init__(self):
        super(RemotePositionCommand, self).__init__(name='CheckPosition')
        self.__get_remote_shares_cmd = GetRemotePositionCommand(self.__check)
        self._state = State(StartConf.PublishKey, Sys.ServerApp, self.name)
        self._state.set_state('last_check_time', None)

    @staticmethod
    def __get_local_shares():
        shares = {Shares.Long: {}, Shares.Short: {}}
        for strategy in StrategyWidget.SHARES:
            strategy_shares = StrategyWidget.get_shares_mgr(strategy).get_shares()
            for los in strategy_shares:
                for ins in strategy_shares[los]:
                    shares[los][ins] = shares[los].get(ins, 0) + strategy_shares[los][ins]
        return shares

    def __check(self, remote_shares):
        diff = {}
        local_shares = self.__get_local_shares()
        for los in local_shares:
            for ins in local_shares[los]:
                if local_shares[los].get(ins, 0) != remote_shares[los].get(ins, 0):
                    if diff.get(los) is None:
                        diff[los] = {}
                    diff[los][ins] = {'local': local_shares[los].get(ins, 0),
                                      'remote': remote_shares[los].get(ins, 0)}

        for los in remote_shares:
            for ins in remote_shares[los]:
                if remote_shares[los].get(ins, 0) != local_shares[los].get(ins, 0):
                    if diff.get(los) is None:
                        diff[los] = {}
                    diff[los][ins] = {'local': local_shares[los].get(ins, 0),
                                      'remote': remote_shares[los].get(ins, 0)}

        l = []
        for los in diff:
            for ins in diff[los]:
                l.append('{} {} local:{} remote:{}'.format(los, ins, diff[los][ins]['local'], diff[los][ins]['remote']))
        if len(l) != 0:
            Monitor.get_server_log(self.name).ERR(msg=str(l))
        Monitor.get_server_log(self.name).INFO(msg=str(l))
        self._state.set_state('last_check_time', str(datetime.datetime.now())[:19])

    def execute(self):
        self.__get_remote_shares_cmd.execute()


class IntervalRemotePositionCommand(AtDateTimeCommand):
    def __init__(self):
        at_datetime = datetime.datetime.combine(datetime.datetime.now().date(),
                                                MonitorServerConf.remote_position_check_time)
        if datetime.datetime.now().time() > MonitorServerConf.remote_position_check_time:
            at_datetime = at_datetime + datetime.timedelta(days=1)
        super(IntervalRemotePositionCommand, self).__init__(at_datetime, RemotePositionCommand())

    def execute(self):
        super(IntervalRemotePositionCommand, self).execute()
        IntervalRemotePositionCommand()
