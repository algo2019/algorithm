from Common.Event import MarkEvent as Event

ORDER_STATE_CHANGE = {}
ON_RTN_ORDER = {}
ON_RTN_TRADE = {}
SHARES_CHANGE = Event()


def get_shares_change():
    return SHARES_CHANGE


def get_order_state_change(strategy_name):
    if ORDER_STATE_CHANGE.get(strategy_name) is None:
        ORDER_STATE_CHANGE[strategy_name] = Event()
    return ORDER_STATE_CHANGE[strategy_name]


def get_on_rtn_order(strategy_name):
    if ON_RTN_ORDER.get(strategy_name) is None:
        ON_RTN_ORDER[strategy_name] = Event()
    return ON_RTN_ORDER[strategy_name]


def get_on_rtn_trade(strategy_name):
    if ON_RTN_TRADE.get(strategy_name) is None:
        ON_RTN_TRADE[strategy_name] = Event()
    return ON_RTN_TRADE[strategy_name]
