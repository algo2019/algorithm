import jrpc

from RemoteControl.CallAction.BaseAction import BaseAction
from TradeEngine.GlobleConf import RemoteStrategy as RSK
from TradeEngine.GlobleConf import SysEvents, StrategyWidget, SysWidget, StrategyEvent, Sys
from TradeEngine.MonitorClient import Monitor
import traceback
from functools import wraps


def locolerr(func):
    logger = SysWidget.get_logger('RemoteService')

    @wraps(func)
    def rt(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger.error(traceback.format_exc())
            raise

    return rt


class RemoteService(jrpc.service.SocketObject):
    def __init__(self, port, host='', debug=False, timeout=None, reuseaddr=True):
        super(RemoteService, self).__init__(port, host, debug, timeout, reuseaddr)
        SysEvents.AdjustStateChange.subscribe(self.__adjust_state_return)
        self._logger = Monitor.get_server_log('RemoteService')

    def start(self):
        try:
            self.setDaemon(True)
            self.pre_run()
            self.running = True
            super(RemoteService, self).start()
        except:
            self.close()
            raise

    @jrpc.service.method
    @locolerr
    def strategy_start(self, strategy, obj_name, instruments):
        self._logger.INFO(strategy, 'strategy: %s obj: %s register : %s', strategy, obj_name,
                          str(instruments))
        StrategyWidget.get_account_mgr(strategy)
        SysWidget.get_tick_data().add_instruments(instruments)

    @jrpc.service.method
    @locolerr
    def adjust_to(self, *args, **kwargs):
        Sys.time_profile_end(args[0], args[1], 'jrpc')
        Sys.time_profile_init(args[0], args[1], 'remote_adjust_to')
        SysWidget.get_adjust_operator().adjust_to(*args, **kwargs)
        Sys.time_profile_end(args[0], args[1], 'remote_adjust_to')

    @jrpc.service.method
    @locolerr
    def insert_order(self, strategy_name, name, instrument, offset, trade_side, volume, price=None, time_out=0,
                     order_price_type='2', time_condition='3', contingent_condition='1', is_local=False):
        Sys.time_profile_init(strategy_name, name, 'remote_insert_order')
        StrategyEvent.get_order_state_change(strategy_name).subscribe(self.__on_order_state_change)
        insert_args = SysWidget.get_trade_client().get_insert_args(strategy_name, name, instrument, offset, trade_side,
                                                                   volume, price, time_out, order_price_type,
                                                                   time_condition, contingent_condition, is_local)
        local_ref = SysWidget.get_trade_client().insert_order(insert_args)
        self._logger.INFO(strategy_name, 'name : %s insert_order rt ref:%s', name, local_ref)
        BaseAction._return(strategy_name, name, RSK.INSERT_ORDER, local_ref)
        Sys.time_profile_end(strategy_name, name, 'remote_insert_order')
        return local_ref

    @staticmethod
    @locolerr
    def __adjust_state_return(state):
        BaseAction._return(state.strategy_name, state.obj_name, RSK.ADJUST_STATE, state)

    def __on_order_state_change(self, order):
        mapper = SysWidget.get_local_remote_ref_mapper()
        base_order = order.copy_unit()
        obj_name = mapper.get_strategy_object_name(order.order_ref)
        self._logger.INFO(order.strategy_name, 'name : %s on_order_state_change : %s', obj_name,
                          base_order.state.string)
        BaseAction._return(order.strategy_name, obj_name, RSK.ORDER_STATE_CHANGE, base_order)
