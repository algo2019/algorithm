import datetime

from Common.Command import Command, IntervalTradingDayCommand
from TradeEngine.GlobleConf import StrategyWidget, InfoUpdaterConf, SysWidget, StartConf


class RecordIncomeCommand(Command):
    def __init__(self):
        super(RecordIncomeCommand, self).__init__(name='RecordIncomeCommand')
        self._total_income = 0
        self.__dao = SysWidget.get_data_item_dao()

    def execute(self):
        self._total_income = 0
        try:
            self._record_strategis()
            self._record_total()
        except RuntimeError as e:
            if str(e) != 'dictionary changed size during iteration':
                raise
            self.execute()

    def _record_strategis(self):
        for strategy in StrategyWidget.ACCOUNT:
            mgr = StrategyWidget.get_account_mgr(strategy)
            income = mgr.interests - mgr.start_cash
            self._total_income += income
            self.__dao.put(StartConf.PublishKey, strategy, 'Income', datetime.datetime.now(), income)

    def _record_total(self):
        self.__dao.put(StartConf.PublishKey, InfoUpdaterConf.total_account_name, 'Income', datetime.datetime.now(),
                       self._total_income)


def start_command():
    IntervalTradingDayCommand(InfoUpdaterConf.income_of_strategy_record_time, RecordIncomeCommand())
