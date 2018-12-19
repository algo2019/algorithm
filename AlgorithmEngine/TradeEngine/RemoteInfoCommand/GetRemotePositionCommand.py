from Common.Command import Command
from TradeEngine.GlobleConf import SysWidget


class GetRemotePositionCommand(Command):
    def __init__(self, call_back):
        super(GetRemotePositionCommand, self).__init__(name='GetRemotePositionCommand')
        self._call_back = call_back

    def execute(self):
        client = SysWidget.get_trade_client()
        client.subscribe_rtn_position(self.__calculate_shares)
        client.req_qry_investor_position_detail(self.name)

    def __calculate_shares(self, data):
        self._call_back(data)
        SysWidget.get_trade_client().unsubscribe_rtn_position(self.__calculate_shares)
