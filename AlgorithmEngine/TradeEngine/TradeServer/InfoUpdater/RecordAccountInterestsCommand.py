import datetime

from Common.Command import Command, IntervalTradingDayCommand
from TradeEngine.GlobleConf import InfoUpdaterConf, SysWidget, StartConf, Sys


class RecordAccountInterestsCommand(Command):
    def __init__(self):
        super(RecordAccountInterestsCommand, self).__init__(name='RecordAccountInterestsCommand')

    def execute(self):
        remote_account = InfoUpdaterConf.get_update_remote_account_writer().read()
        SysWidget.get_data_item_dao().put(StartConf.PublishKey, Sys.ServerApp, 'AccountInterests', datetime.datetime.now(),
                                          remote_account['Interests'])


def start_command():
    IntervalTradingDayCommand(InfoUpdaterConf.close_time, RecordAccountInterestsCommand())
