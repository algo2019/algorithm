import datetime
import traceback

from Common.Command import Command, IntervalTradingDayCommand
from TradeEngine.GlobleConf import StartConf
from TradeEngine.GlobleConf import StrategyWidget, SysWidget
from TradeEngine.MonitorClient import Monitor
from TradeEngine.GlobleConf import InfoUpdaterConf


class RecordInterestsCommand(Command):
    def __init__(self):
        super(RecordInterestsCommand, self).__init__(name='RecordInterestsCommand')
        self.__total_name = InfoUpdaterConf.total_account_name
        self.__dao = SysWidget.get_data_item_dao()

    def execute(self):
        Monitor.get_server_log(self.name).INFO(msg='start execute')
        total_interests = 0
        total_cost = 0
        now_date = datetime.datetime.now().date()
        try:
            for strategy in StrategyWidget.ACCOUNT:
                try:
                    mgr = StrategyWidget.get_account_mgr(strategy)
                    interests = mgr.interests
                    cost = mgr.start_cash
                    total_interests += interests
                    total_cost += cost
                    self.__dao.put(StartConf.PublishKey, strategy, 'Interests', now_date, interests)
                    self.__dao.put(StartConf.PublishKey, strategy, 'IncomeRate', now_date,
                                   (interests - cost) / cost * 100)
                except:
                    Monitor.get_server_log(self.name).ERR(strategy, traceback.format_exc())
        except RuntimeError as e:
            if str(e) != 'dictionary changed size during iteration':
                raise
            Monitor.get_server_log(self.name).INFO(msg='re_execute')
            self.execute()
        if total_cost == 0:
            interests_rate = 0
        else:
            interests_rate = (total_interests - total_cost) / total_cost * 100

        self.__dao.put(StartConf.PublishKey, self.__total_name, 'Interests', now_date, total_interests)
        self.__dao.put(StartConf.PublishKey, self.__total_name, 'IncomeRate', now_date, interests_rate)
        Monitor.get_server_log(self.name).INFO(msg='execute over')


def start_command():
    IntervalTradingDayCommand(InfoUpdaterConf.interests_record_time, RecordInterestsCommand())
