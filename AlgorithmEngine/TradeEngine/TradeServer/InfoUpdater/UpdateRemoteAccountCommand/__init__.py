from Common.Command import Command, TradingTimeIntervalCommand
from TradeEngine.GlobleConf import InfoUpdaterConf, SysWidget


class UpdateRemoteAccountCommand(Command):
    def __init__(self):
        super(UpdateRemoteAccountCommand, self).__init__(name='UpdateRemoteAccountCommand')
        SysWidget.get_trade_client().subscribe_rtn_account(self.__write)

    def __write(self, remote_account):
        static_interests = remote_account['PreBalance'] - remote_account['PreMortgage'] - remote_account['PreCredit'] + \
                           remote_account['Mortgage'] + remote_account['Deposit'] - remote_account['Withdraw']
        interests = static_interests + remote_account['CloseProfit'] + remote_account['PositionProfit'] - \
                    remote_account['Commission']
        remote_account['Interests'] = interests
        remote_account['StaticInterests'] = static_interests
        InfoUpdaterConf.get_update_remote_account_writer().write(remote_account)

    def execute(self):
        SysWidget.get_trade_client().req_qry_trading_account(None)


def start_command():
    TradingTimeIntervalCommand(InfoUpdaterConf.interval, UpdateRemoteAccountCommand())
