# -*- coding: utf-8 -*-
"""
orderinsertcheckconfig.py
"""

from Common.Command import Command
from TradeEngine.GlobleConf import OnRtnOrderState, StrategyWidget, Sys
from TradeEngine.TradeServer.RtnMsgMaker import RtnMsgMaker

from .insertargs import InsertArgs
from .tradeclientfactory import factory


logger = factory.service_logger('OrderInsertCheck')


class CheckRes(Command):
    """
    CheckRes
    """

    def __init__(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> None
        super(CheckRes, self).__init__(name='CheckRes:ref' + local_ref)
        self._local_ref = local_ref
        self._insert_args = insert_args

    @property
    def _client(self):
        # type: () -> factory.ctp_trade_client
        return factory.ctp_trade_client

    def _execute_log(self):
        # type: () -> None
        logger.INFO(self._insert_args.strategy_name, '%s excuse', str(self))

    def exception_handle(self, e):
        # type: (Exception) -> None
        """
        :param e:
        """
        from TradeEngine.MonitorClient import Monitor
        import traceback
        Monitor.get_server_log(self.name).ERR(self._insert_args.strategy_name, traceback.format_exc())

    def execute(self):
        # type: () -> None
        """
        execute
        """
        self._execute_log()
        super(CheckRes, self).execute()


class Canceled(CheckRes):
    """
    Canceled
    """
    def execute(self):
        # type: () -> None
        """
        execute
        """
        Sys.time_profile(self._insert_args.strategy_name, self._insert_args.strategy_name, 'insert_order', 'canceled')
        self._execute_log()
        RtnMsgMaker.send_rtn_order_event(self._insert_args.strategy_name, self._local_ref, OnRtnOrderState.CANCELED, 0,
                                         self._insert_args.volume)
        Sys.time_profile_end(self._insert_args.strategy_name, self._insert_args.strategy_name, 'insert_order')

    def __str__(self):
        # type: () -> str
        return 'CheckRes:Canceled'


class InsertOpen(CheckRes):
    """
    InsertOpen
    """
    def execute(self):
        # type: () -> None
        """
        execute
        """
        Sys.time_profile_init(self._insert_args.strategy_name, self._insert_args.strategy_name, 'InsertOpen')
        self._execute_log()
        self._client.insert_order(self._local_ref, self._insert_args)
        Sys.time_profile_end(self._insert_args.strategy_name, self._insert_args.strategy_name, 'InsertOpen')

    def __str__(self):
        # type: () -> str
        return 'CheckRes:InsertOpen'


class InsertClose(CheckRes):
    """
    InsertClose
    """
    def execute(self):
        # type: () -> None
        """
        execute
        """
        Sys.time_profile_init(self._insert_args.strategy_name, self._insert_args.strategy_name, 'InsertClose')
        self._execute_log()
        factory.close_trade_client.cover_order(self._local_ref, self._insert_args)
        Sys.time_profile_end(self._insert_args.strategy_name, self._insert_args.strategy_name, 'InsertClose')

    def __str__(self):
        # type: () -> str
        return 'CheckRes:InsertClose'


class check_value(object):
    """
    config
    """
    last_open_time = 0


def __check_cash(local_ref, insert_args):
    # type: (str, InsertArgs) -> CheckRes or bool
    account_mgr = StrategyWidget.get_account_mgr(insert_args.strategy_name)
    if account_mgr.get_cash_of_no_ref(local_ref) >= account_mgr._commission(insert_args.strategy_name,
                                                                            insert_args.price,
                                                                            insert_args.volume):
        logger.INFO(insert_args.strategy_name, '__check_cash res:true')
        return True
    else:
        logger.ERR(insert_args.strategy_name, 'strategy %s %s open cash:hold %2.2f need %2.2f',
                   insert_args.strategy_name,
                   insert_args.instrument,
                   account_mgr.get_cash_of_no_ref(local_ref),
                   account_mgr._commission(insert_args.instrument, insert_args.price, insert_args.volume))
        logger.INFO(insert_args.strategy_name, '__check_cash res:need more cash')
        return Canceled(local_ref, insert_args)


__check_open_list = [
    __check_cash,
]


def open_insert_check(local_ref, insert_args):
    # type: (str, InsertArgs) -> CheckRes or bool
    """
    :param local_ref:
    :param insert_args:
    :return:
    """
    for check_func in __check_open_list:
        rt = check_func(local_ref, insert_args)
        if rt is not True:
            return rt
    return InsertOpen(local_ref, insert_args)


def __check_shares(local_ref, insert_args):
    # type: (str, InsertArgs) -> CheckRes or bool
    share_mgr = StrategyWidget.get_shares_mgr(insert_args.strategy_name)
    if share_mgr.get_shares(insert_args.instrument, insert_args.long_or_short) >= insert_args.volume:
        logger.INFO(insert_args.strategy_name, '__check_shares res:true')
        return True
    else:
        logger.ERR(insert_args.strategy_name, 'strategy %s %s los:%s cover share:hold %d wanted %d',
                   insert_args.strategy_name,
                   insert_args.instrument, insert_args.long_or_short,
                   share_mgr.get_shares(insert_args.instrument, insert_args.long_or_short), insert_args.volume)
        logger.INFO(insert_args.strategy_name, '__check_shares res:shares err')
        return Canceled(local_ref, insert_args)


__check_cover_check = [
    __check_shares,
]


def cover_insert_check(local_ref, insert_args):
    # type: (str, InsertArgs) -> CheckRes or bool
    """
    :param local_ref:
    :param insert_args:
    :return:
    """
    for check_func in __check_cover_check:
        rt = check_func(local_ref, insert_args)
        if rt is not True:
            return rt
    return InsertClose(local_ref, insert_args)


def check_insert(local_ref, insert_args):
    # type: (str, InsertArgs) -> CheckRes or bool
    """
    :param local_ref:
    :param insert_args:
    :return:
    """
    if insert_args.is_open():
        logger.INFO(insert_args.strategy_name, 'check for open')
        return open_insert_check(local_ref, insert_args)
    else:
        logger.INFO(insert_args.strategy_name, 'check for close')
        return cover_insert_check(local_ref, insert_args)
