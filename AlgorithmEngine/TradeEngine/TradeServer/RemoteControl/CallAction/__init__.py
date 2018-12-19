from CanceledOrderAction import CanceledOrderAction
from ChangeStartCashAction import ChangeStartCashAction
from TradeEngine.GlobleConf import RemoteStrategy as RSK

action_table = {
    RSK.CANCELED_ORDER: CanceledOrderAction,
    RSK.CHANGE_START_CASH: ChangeStartCashAction,
}


def get_action(cmd, strategy, obj_name, args, kwargs):
    return action_table[cmd](strategy, obj_name, args, kwargs)
