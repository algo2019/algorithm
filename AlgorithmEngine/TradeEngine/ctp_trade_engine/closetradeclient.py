# -*- coding: utf-8 -*-
"""
closetradeclient.py
"""
from MarketDataServer import mkdata_tools
from TradeEngine.GlobleConf import Sys
from TradeEngine.TradeServer import Order
from TradeEngine.TradeServer.RtnMsgMaker import RtnMsgMaker
from TradeEngine.GlobleConf import OffSet, StrategyWidget, OnRtnOrderState, SysWidget
from TradeEngine.GlobleConf import SysEvents

from .insertargs import InsertArgs
from .tradeclientfactory import factory


class CloseTradeClient(object):
    """
    CloseTradeClient
    """

    def __init__(self, thrift_client):
        # type: (thrift_client) -> None
        self.__intercept = []
        self.__client = thrift_client
        self._check_order_close_thread = None
        self.__started = False
        self.__logger = factory.service_logger('CloseTradeClient')
        SysEvents.OrderOver.subscribe(self.__on_order_over, Sys.Sys)

    def cover_order(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> None
        """
        :param local_ref:
        :param insert_args:
        """
        Sys.time_profile_init(insert_args.strategy_name, insert_args.name, 'cover')

        if mkdata_tools.get_exchange_id(insert_args.instrument) == 'SHFX':
            self.__cover_shfe(local_ref, insert_args)
        else:
            self.__client.insert_order(local_ref, insert_args)
        Sys.time_profile_end(insert_args.strategy_name, insert_args.name, 'cover')

    def __cover_shfe(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> None
        share_mgr = StrategyWidget.get_shares_mgr(insert_args.strategy_name)
        today_shares = share_mgr.get_today_shares(insert_args.instrument, insert_args.long_or_short)
        self.__logger.INFO(insert_args.strategy_name, 'Cover:SHFE - todayShores : %d cover: %d', today_shares,
                           insert_args.volume)
        if today_shares == 0:
            self.__client.insert_order(local_ref, insert_args)
        elif today_shares >= insert_args.volume:
            self.__client.insert_order(local_ref, insert_args.copy_args(offset=OffSet.CloseToday))
        else:
            Sys.time_profile_init(insert_args.strategy_name, insert_args.name, 'cover_shfe')
            insert_args2 = insert_args.copy_args(volume=insert_args.volume - today_shares)
            insert_args3 = insert_args.copy_args(offset=OffSet.CloseToday, volume=today_shares)
            self.__intercept.append(
                [local_ref, SysWidget.get_trade_client().insert_order(insert_args3, is_sys=True), False, insert_args2,
                 insert_args])

    def __on_order_over(self, order):
        # type: (Order) -> None
        for intercept in self.__intercept:
            if intercept[1] == order.order_ref:
                self.__on_process_intercept(intercept, order)

    def __on_process_intercept(self, intercept, order):
        # type: (list, Order) -> None
        local_ref, self_ref, cover_today_ok, insert_args2, insert_args = intercept
        self.__send_rtn_trade_event(local_ref, insert_args, order)
        if not cover_today_ok:
            intercept[2] = True
            if order.is_filled():
                self.__on_intercept_filled(intercept)
            elif order.is_canceled():
                self.__on_intercept_canceled(local_ref, insert_args, order)
                self.__intercept.remove(intercept)
            else:
                self.__logger.ERR(insert_args.strategy_name, 'CoverSHFX:order state:%s' % order.state.string)
                self.__on_intercept_canceled(local_ref, insert_args, order)
                self.__intercept.remove(intercept)
            Sys.time_profile(insert_args.strategy_name, insert_args.name, 'cover_shfe', 'cover2')
        else:
            filled_volume = insert_args.volume - (order.volume - order.filled_volume)
            if order.is_filled():
                order_state = OnRtnOrderState.FILLED
            elif order.is_canceled():
                order_state = OnRtnOrderState.CANCELED
            else:
                self.__logger.ERR(insert_args.strategy_name, 'CoverSHFX:order state:%s' % order.state.string)
                order_state = OnRtnOrderState.CANCELED
            RtnMsgMaker.send_rtn_order_event(insert_args.strategy_name, local_ref, order_state, filled_volume,
                                             insert_args.volume)
            self.__intercept.remove(intercept)
            Sys.time_profile_end(insert_args.strategy_name, insert_args.name, 'cover_shfe')

    @staticmethod
    def __send_rtn_trade_event(local_ref, insert_args, order):
        # type: (str, InsertArgs, Order) -> None
        RtnMsgMaker.send_rtn_trade_event(insert_args.strategy_name, local_ref, None,
                                         insert_args.copy_args(price=order.filled_price, volume=order.filled_volume))

    @staticmethod
    def __on_intercept_filled(intercept):
        # type: (list) -> None
        local_ref, self_ref, cover_today_ok, insert_args2, insert_args = intercept
        intercept[1] = SysWidget.get_trade_client().insert_order(insert_args2, is_sys=True)

    @staticmethod
    def __on_intercept_canceled(local_ref, insert_args, order):
        # type: (str, InsertArgs, Order) -> None
        RtnMsgMaker.send_rtn_order_event(insert_args.strategy_name, local_ref, OnRtnOrderState.CANCELED,
                                         order.filled_volume, insert_args.volume)
