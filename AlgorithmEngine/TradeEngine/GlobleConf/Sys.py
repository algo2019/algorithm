from RedisKey import DB
from TradeEngine.GlobleConf import StartConf
from Common.TimeProfile import time_profile, time_profile_end, time_profile_init
from Common.TimeProfile import Config as TimeProfileConfig

__all__ = ['time_profile', 'time_profile_end', 'time_profile_init', 'TimeProfileConfig', 'ServerApp', 'Sys',
           'Shares', 'Account', 'Stoped', 'Debug', 'AnalogTradeClient', 'is_active_strategy', 'sys_config_init']


TimeProfileConfig.TimeProfile = False
ServerApp = 'total'
Sys = DB.Strategy.Sys()
Shares = DB.Strategy.Shares()
Account = DB.Strategy.Account()
Stoped = False
Debug = False
AnalogTradeClient = False


class _L(object):
    strategy_table = None


def is_active_strategy(strategy):
    from TradeEngine.GlobleConf import StrategyWidget
    if strategy in StrategyWidget.ACCOUNT:
        return True
    else:
        if _L.strategy_table is None:
            from Tables import StrategyTable
            _L.strategy_table = StrategyTable.create()
        strategis = _L.strategy_table.get_strategy_of_sys(StartConf.PublishKey)
        if strategy in strategis:
            StrategyWidget.register_strategy([strategy])
            return True
        return False


def sys_config_init():
    from Common.AtTimeObjectEngine import ThreadEngine, BaseExceptionHandler
    from TradeEngine.MonitorClient import Monitor

    class ExceptionHandler(BaseExceptionHandler):
        def __init__(self):
            self.logger = Monitor.get_server_log('EngineExceptionHander')

        def process(self, engine, cmd, e):
            import traceback
            self.logger.ERR(engine.name, traceback.format_exc())

    ThreadEngine.exception_handler = ExceptionHandler()

    from Common.TimeProfile import Handler, Config, Filter, add_filter

    class SysTimeProfileHandler(Handler):
        def __init__(self):
            self.log = Monitor.get_logger('SysTimeProfile')

        def process(self, system, name, item, timestamp):
            self.log.publish('TIME_PROFILE', '{} {}: {:f}'.format(name, item, timestamp))

    Config.Handler = SysTimeProfileHandler()

    class TimeProfileFilter(Filter):
        def process(self, strategy, name, item):
            try:
                if item in {'on_tick', 'adjust_to', 'Order', 'update_filled_volume', 'bar_price',
                            'mk_min', 'min_process', 'min_strategy', 'filled_price', 'TradeSide'}:
                    return True
                return False
            except Exception as e:
                from TradeEngine.MonitorClient.Monitor import get_server_log
                Monitor.get_server_log('TimeProfileFilter').ERR(msg=str(e))

    add_filter(TimeProfileFilter())

    def hd_send(order):
        if order.is_filled():
            time_profile(order.strategy_name, order.instrument, 'filled_price', order.filled_price)

    from TradeEngine.GlobleConf import SysEvents
    SysEvents.OrderOver.subscribe(hd_send)

    TimeProfileConfig.TimeProfile = True
