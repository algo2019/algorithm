from TradeEngine.GlobleConf import SysWidget, Shares
from TradeEngine.GlobleConf.RedisKey import Publish
from TradeEngine.MonitorClient import Monitor
from TradeEngine.RemoteInfoCommand import RemoteInfoCommand


class GetRemoteAccountCommand(RemoteInfoCommand):
    def __init__(self, call_back):
        super(GetRemoteAccountCommand, self).__init__(call_back, Publish.RemoteAccount(), 'GetRemoteAccountCommand')

    def execute(self):
        self._sub_event.subscribe(self.__parse)
        SysWidget.get_trade_client().req_qry_trading_account(self.name)

    def __parse(self, data):
        ds = data['data'].split('#')
        self._sub_event.unsubscribe(self.__parse)
        if ds[0] == 'ACCOUNT':
            Available, Mortgage, PositionProfit, CloseProfit, PreBalance, PreCredit, PreMortgage, Deposit, Withdraw, Commission = map(
                float, ds[1:])
            rt = {
                'Available': Available,
                'Mortgage': Mortgage,
                'PositionProfit': PositionProfit,
                'CloseProfit': CloseProfit,
                'PreBalance': PreBalance,
                'PreCredit': PreCredit,
                'PreMortgage': PreMortgage,
                'Deposit': Deposit,
                'Withdraw': Withdraw,
                'Commission': Commission
            }
            self._call_back(rt)
        elif ds[0] == 'ERR':
            Monitor.get_server_log(self.name).ERR(msg=ds[1])
