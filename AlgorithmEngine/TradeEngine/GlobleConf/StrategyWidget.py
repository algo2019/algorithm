from TradeEngine.GlobleConf import Sys

SHARES = {}
ACCOUNT = {}


def get_shares_mgr(strategy_name):
    if SHARES.get(strategy_name) is None:
        raise Exception('unknown strategy heartbeat %s' % strategy_name)
    return SHARES[strategy_name]


def get_account_mgr(strategy_name):
    if ACCOUNT.get(strategy_name) is None:
        raise Exception('unknown strategy heartbeat %s' % strategy_name)
    return ACCOUNT[strategy_name]


def register_strategy(strategy_list):
    for strategy_name in strategy_list:
        if ACCOUNT.get(strategy_name) is None:
            strategy_name = str(strategy_name)
            from TradeEngine.TradeServer import Shares as ShareMgr
            SHARES[strategy_name] = ShareMgr.Shares(strategy_name)
            from TradeEngine.TradeServer import Account
            ACCOUNT[strategy_name] = Account.Account(strategy_name)
