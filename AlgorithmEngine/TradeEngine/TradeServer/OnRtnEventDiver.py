# coding=utf-8
import json

from Common.Command import Command, SleepCommand
from TradeEngine.GlobleConf import OnRtnOrderState
from TradeEngine.GlobleConf import StrategyEvent
from TradeEngine.GlobleConf import Sys
from TradeEngine.GlobleConf import SysWidget
from TradeEngine.TradeServer import Order
from TradeEngine.TradeServer.OrderUnit import OrderUnit
from tools import format_to_datetime


def warp_char(int_or_str):
    if isinstance(int_or_str, basestring):
        return int_or_str
    if type(int_or_str) == int:
        return chr(int_or_str)

class OnRtnTrade(OrderUnit):
    def __init__(self, arg):
        super(OnRtnTrade, self).__init__(arg['InstrumentID'], warp_char(arg['OffsetFlag']), warp_char(arg['Direction']),
                                         arg['Price'], arg['Volume'])
        self.__rtn_info = arg

    @property
    def trade_id(self):
        return self.__rtn_info.get('TradeID')

    @property
    def trading_day(self):
        return format_to_datetime(self.__rtn_info['TradingDay'])

    @property
    def order_ref(self):
        return str(self.__rtn_info['OrderRef'])


class OnRtnOrder(object):
    def __init__(self, arg):
        self.__rtn_info = arg

    @property
    def state(self):
        return warp_char(self.__rtn_info['OrderStatus'])

    @property
    def state_msg(self):
        return self.__rtn_info['StatusMsg'].decode('gb2312').encode('utf8')

    @property
    def order_ref(self):
        return str(self.__rtn_info['OrderRef'])

    @property
    def traded_volume(self):
        return self.__rtn_info['VolumeTraded']

    @property
    def remain_volume(self):
        return self.__rtn_info['VolumeTotal']


class OnRtnEventDiver(object):
    def __init__(self):
        self.__mapper = SysWidget.get_local_remote_ref_mapper()
        self.__logger = SysWidget.get_service_logger('OnRtnUpdater')
        self.__on_rtn_order_info = {}
        self.__trade_ids = set()
        self.__started = False
        self.__max_try = 5
        self.__logger.INFO(msg='init ok')

    def start(self):
        if not self.__started:
            self.__started = True
            SysWidget.get_trade_client().subscribe_rtn_order(self.__on_rtn_order)
            SysWidget.get_trade_client().subscribe_rtn_trade(self.__on_rtn_trade)
            self.__logger.INFO(msg='started')

    def stop(self):
        if self.__started:
            self.__started = False
            SysWidget.get_trade_client().subscribe_rtn_trade(self.__on_rtn_trade)
            SysWidget.get_trade_client().subscribe_rtn_order(self.__on_rtn_order)

    def reset(self):
        self.__trade_ids.clear()
        self.__logger.INFO(msg='reset')

    @classmethod
    def parse(cls, msg_data):
        return {item[0]: item[1] for item in (i.split('#') for i in str(msg_data).split('|'))}

    def __on_rtn_trade(self, data):
        Sys.time_profile_init('OnRtnDriver', 'OnRtn', 'on_rtn_trade')
        trade = OnRtnTrade(data)
        try:
            strategy = self.__mapper.get_strategy_name(trade.order_ref)
            obj_name = self.__mapper.get_strategy_object_name(trade.order_ref)
        except :
            self.__logger.WARN(msg='onRtnTrade:unknown ref %s' % str(trade.order_ref))
            Sys.time_profile_end('OnRtnDriver', 'OnRtn', 'on_rtn_trade')
            return

        self.__logger.INFO(strategy, 'name: %s onRtnTrade - OrderRef:%s Volume:%d Price:%2.2f', obj_name,
                           trade.order_ref, trade.volume, trade.price)
        trade_key = '{}.{}'.format(trade.order_ref, trade.trade_id)
        if trade_key not in self.__trade_ids:
            self.__trade_ids.add(trade_key)
            StrategyEvent.get_on_rtn_trade(self.__mapper.get_strategy_name(trade.order_ref)).emit(trade)
        Sys.time_profile_end('OnRtnDriver', 'OnRtn', 'on_rtn_trade')

    def __wait_order_over(self, order, d):
        if order.is_filled():
            d['Price'] = order.filled_price
            self.__logger.INFO(msg='[TIME]|{}|'.format(json.dumps(d)))
            return
        if order.is_canceled():
            return

        SleepCommand(1, Command(target=self.__wait_order_over, args=(order, d)), SysWidget.get_external_engine())

    def __on_rtn_order(self, data):
        Sys.time_profile_init('OnRtnDriver', 'OnRtn', 'on_rtn_order')
        rtn_order = OnRtnOrder(data)
        try:
            strategy = self.__mapper.get_strategy_name(rtn_order.order_ref)
            obj_name = self.__mapper.get_strategy_object_name(rtn_order.order_ref)
        except Exception as e:
            self.__logger.WARN(msg='onRtnOrder:err {}'.format(str(e)))
            Sys.time_profile_end('OnRtnDriver', 'OnRtn', 'on_rtn_order')
            return

        self.__logger.INFO(strategy,
                           'name: %s onRtnOrder - OrderRef:%s OrderStatus:%s VolumeTraded:%s RemainTotal:%s %s',
                           obj_name, rtn_order.order_ref, rtn_order.state, rtn_order.traded_volume,
                           rtn_order.remain_volume, rtn_order.state_msg)
        if rtn_order.state == '6':
            self.__logger.ERR(strategy, 'TradeEngineErr : %s', rtn_order.state_msg)
        self.emit_rtn_order_event(rtn_order)
        Sys.time_profile_end('OnRtnDriver', 'OnRtn', 'on_rtn_order')

    @classmethod
    def emit_rtn_order_event(cls, rtn_order):
        order_event = StrategyEvent.get_on_rtn_order(
            SysWidget.get_local_remote_ref_mapper().get_strategy_name(rtn_order.order_ref))
        if rtn_order.state == OnRtnOrderState.ACCEPTED:
            order_event.emit(rtn_order, Order.ACCEPTED)
        elif rtn_order.state in OnRtnOrderState.CANCELED_SET:
            order_event.emit(rtn_order, Order.CANCELED)
