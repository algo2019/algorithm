# -*- coding: utf-8 -*-
"""
tradeclient.py
"""

from Common.Event import MarkEvent
from TradeEngine.GlobleConf import SysWidget, StrategyWidget, Sys
from TradeEngine.TradeServer.Order import Order
from TradeEngine.TradeServer.RtnMsgMaker import RtnMsgMaker
from . import orderinsertcheckconfig
from .insertargs import InsertArgs
from .tradeclientfactory import factory


class TradeClient(object):
    """
    ctp_trade_engine
    """

    def __init__(self):
        # type: () -> None
        self.__logger = factory.service_logger('TradeClient')
        self.__mapper = SysWidget.get_local_remote_ref_mapper()

    def insert_order(self, insert_args, is_sys=False):
        # type: (InsertArgs, bool) -> str
        """
        :param insert_args:
        :param is_sys:
        :return: local_ref
        """
        Sys.time_profile_init(insert_args.strategy_name, insert_args.name, 'insert_order')
        self.__logger.INFO(insert_args.strategy_name, 'insert_order %s %s %s %d', insert_args.instrument,
                           insert_args.offset, insert_args.trade_side, insert_args.volume)
        StrategyWidget.get_account_mgr(insert_args.strategy_name)
        local_ref = RtnMsgMaker.next_id()
        self.__mapper.set(local_ref, insert_args.strategy_name, insert_args.name, insert_args.instrument)
        order = Order(local_ref, insert_args.instrument, insert_args.offset, insert_args.trade_side, insert_args.price,
                      insert_args.volume)
        if is_sys:
            setattr(order, MarkEvent.mark_name, Sys.Sys)
        orderinsertcheckconfig.check_insert(local_ref, insert_args).execute()
        Sys.time_profile_end(insert_args.strategy_name, insert_args.name, 'insert_order')
        return local_ref

    @classmethod
    def get_insert_args(cls, *args, **kwargs):
        return InsertArgs(*args, **kwargs)

    def __getattr__(self, item):
        # type: (str) -> object
        return factory.ctp_trade_client.__getattribute__(item)
