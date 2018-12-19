from TradeEngine.GlobleConf import StrategyWidget
from BaseAction import BaseAction


class ChangeStartCashAction(BaseAction):

    def execute(self):
        cash_added = float(self._args[0])
        self._logger.INFO(self._strategy, 'Strategy:%s change start cash:%f' % (self._strategy, cash_added))
        StrategyWidget.get_account_mgr(self._strategy).update_start_cash(cash_added)

