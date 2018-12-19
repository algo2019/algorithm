from TradeEngine.GlobleConf import SysWidget
from BaseAction import BaseAction


class CanceledOrderAction(BaseAction):

    def execute(self):
        self._logger.INFO(self._strategy, 'name : %s order canceled', self._obj_name)
        SysWidget.get_trade_client().canceled(*self._args)

