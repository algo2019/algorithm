import datetime
import threading

from Common.Command import Command, SleepCommand
from TradeEngine.GlobleConf import Lock, OnRtnOrderState, StrategyEvent, SysWidget
from TradeEngine.MonitorClient import Monitor
from TradeEngine.OnBarDataStruct import OnBarDataField
from TradeEngine.TradeServer import OnRtnEventDiver
import itertools


class RtnMsgMaker(object):
    __logger = Monitor.get_server_log('RtnMsgMaker')
    __lock = threading.Condition()
    __count = itertools.count(-1, -1)
    __time_delay = 0.01

    @classmethod
    def next_id(cls):
        return str(cls.__count.next())

    @classmethod
    def get_on_rtn_trade_msg(cls, remote_ref, trade_id, order_unit):
        return 'OrderRef#%s|Direction#%s|Price#%s|Volume#%s|TradingDay#%s|TradeID#%s|OffsetFlag#%s|InstrumentID#%s' % (
            remote_ref, order_unit.trade_side, str(order_unit.price), str(order_unit.volume),
            str(datetime.datetime.now().date()), str(trade_id), order_unit.offset, order_unit.instrument)

    @classmethod
    def get_on_rtn_order_msg(cls, remote_ref, order_state, trade_volume, total_volume):
        return 'OrderRef#%s|OrderStatus#%s|VolumeTraded#%d|VolumeTotal#%d' % (
            remote_ref, order_state, int(trade_volume),
            int(total_volume))

    @classmethod
    def get_rtn_trade(cls, local_ref, trade_id, order_unit):
        msg = cls.get_on_rtn_trade_msg(local_ref, trade_id, order_unit)
        return OnRtnEventDiver.OnRtnTrade(OnRtnEventDiver.OnRtnEventDiver.parse(msg))

    @staticmethod
    def _send_rtn_trade_now(strategy_name, trade):
        Lock.ORDER_STATE.acquire()
        StrategyEvent.get_on_rtn_trade(strategy_name).emit(trade)
        Lock.ORDER_STATE.release()

    @classmethod
    def send_rtn_trade_event(cls, strategy_name, local_ref, trade_id, order_unit):
        cls.__logger.INFO(strategy_name, 'send_rtn_trade_event %s %s %s', strategy_name, local_ref, trade_id)
        if trade_id is None:
            trade_id = cls.next_id()
        rtn_trade = cls.get_rtn_trade(local_ref, trade_id, order_unit)
        SleepCommand(cls.__time_delay, Command(target=cls._send_rtn_trade_now, args=(strategy_name, rtn_trade)), SysWidget.get_main_engine())

    @classmethod
    def get_rtn_order(cls, local_ref, order_state, trade_volume, total_volume):
        msg = cls.get_on_rtn_order_msg(local_ref, order_state, trade_volume, total_volume)
        return OnRtnEventDiver.OnRtnOrder(OnRtnEventDiver.OnRtnEventDiver.parse(msg))

    @staticmethod
    def _send_rtn_order_event_now(rtn_order):
        Lock.ORDER_STATE.acquire()
        OnRtnEventDiver.OnRtnEventDiver.emit_rtn_order_event(rtn_order)
        Lock.ORDER_STATE.release()

    @classmethod
    def send_rtn_order_event(cls, strategy_name, local_ref, order_state, trade_volume, total_volume):
        rtn_order = cls.get_rtn_order(local_ref, order_state, trade_volume, total_volume)
        SleepCommand(cls.__time_delay, Command(target=cls._send_rtn_order_event_now, args=(rtn_order, )), SysWidget.get_main_engine())

    @classmethod
    def send_order_state_change_event(cls, strategy_name, order):
        StrategyEvent.get_order_state_change(strategy_name).emit(order)

    @classmethod
    def send_rtn_order_canceled_event(cls, local_ref, filled_volume, total_volume):
        rtn_order = cls.get_rtn_order(local_ref, OnRtnOrderState.CANCELED, filled_volume, total_volume)
        SleepCommand(cls.__time_delay, Command(target=cls._send_rtn_order_event_now, args=(rtn_order, )), SysWidget.get_main_engine())

    @classmethod
    def get_data_msg(cls, kwargs):
        data = ''
        if len(kwargs) != 0:
            data_ = OnRtnEventDiver.OnRtnEventDiver.parse(data)
            for key in kwargs:
                data_[key] = str(kwargs[key])
        return '|'.join(['%s#%s' % (key, kwargs[key]) for key in kwargs])

    @classmethod
    def send_min_data(cls, kwargs):
        publish_key = 'minData.%s.%s'%(kwargs[OnBarDataField.InstrumentID], kwargs[OnBarDataField.Period])
        SysWidget.get_redis_reader().publish(publish_key, cls.get_data_msg(kwargs))
