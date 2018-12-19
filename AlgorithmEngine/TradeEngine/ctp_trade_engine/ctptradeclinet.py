# -*- coding: utf-8 -*-
"""
ctptradeclinet.py
    use ctptradeengine.so to operate ctp
"""
import datetime

from Common.Command import Command, SleepCommand, IntervalDateTimeCommand
from Common.Event import Event
from TradeEngine.GlobleConf import Sys
from TradeEngine.GlobleConf import SysWidget, OnRtnOrderState
from TradeEngine.TradeServer.RtnMsgMaker import RtnMsgMaker

from .insertargs import InsertArgs
from .tradeclientfactory import factory

ctptradeengine = factory.ctptradeengineso

__all__ = ['CTPTradeClient']


class OrderTimeOutCheckCommand(SleepCommand):
    """
    OrderTimeOutCheckCommand
    """

    def __init__(self, timeout, local_ref, ctp_trade_client):
        # type: (int, str, CTPTradeClient) -> None
        if timeout == 0:
            return
        target_cmd = Command(name='OrderTimeOutCheckCommand', target=self.__check_to_cancel)
        super(OrderTimeOutCheckCommand, self).__init__(timeout, target_cmd, SysWidget.get_main_engine())
        self.__local_ref = local_ref
        self.__client = ctp_trade_client

    def __check_to_cancel(self):
        # type: () -> None
        if self.__local_ref in SysWidget.get_active_order_list().handler(
                lambda active_order: map(lambda order: order.order_ref, active_order)):
            self.__client.canceled(self.__local_ref)


class CTPTradeClient(ctptradeengine.TradeServiceSpi):
    """
    CTPTradeClient
    """

    def __init__(self, ctp_trade_host, broker_id, user_id, password, publish_key, redis_host,
                 redis_port, is_local=None):
        # type: (str, int, str, str, str, str) -> None
        self.__host = ctp_trade_host
        self.__broker, self.__user, self.__password = broker_id, user_id, password
        self.__pk = publish_key
        self.__redis_host, self.__redis_port = redis_host, redis_port
        self.__is_local = is_local
        self.__logger = factory.service_logger('CTPTradeClient')
        self.__ref_mapper = SysWidget.get_local_remote_ref_mapper()
        self.__started = False
        self.__restarted = False
        self.__client = None
        self.__set_restart_command()
        self.__on_rtn_order_event = Event()
        self.__on_rtn_trade_event = Event()
        self.__on_rtn_account_event = Event()
        self.__on_rtn_position_event = Event()
        self.__temp = {}

    def restart(self):
        # type: () -> bool
        """
        :return: is_success
        """
        if self.__restarted:
            return False
        self.__restarted = True
        self.__logger.INFO(msg='restart')
        self.stop()
        self.start()
        return True

    def start(self):
        # type: () -> None
        """
        instantiate an object of PyTradeService
        """
        if self.__client is None:
            self.__started = True
            self.__logger.INFO(msg='starting')
            self.__client = ctptradeengine.PyTradeService()
            self.__client.RegisterSpi(self)
            self.__client.start(self.__broker, self.__user, self.__password, self.__host, self.__redis_host,
                                self.__redis_port, self.__pk)
            self.__logger.INFO(msg='started')

    def stop(self):
        # type: () -> None
        """
        delete the object of PyTradeService
        """
        if self.__client is not None:
            self.__client.UnRegisterSpi()
            del self.__client
            self.__client = None
            self.__started = False
            self.__logger.INFO(msg='stoped')

    def on_rtn_trade(self, rtn_trade):
        self.__on_rtn_trade_event.emit(rtn_trade)

    def on_rtn_order(self, rtn_order):
        self.__on_rtn_order_event.emit(rtn_order)

    def on_rtn_trade_account(self, trade_account, rsp_info, rsp_id, is_last):
        self.__on_rtn_account_event.emit(trade_account)

    def insert_analog_order(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> None
        """
        insert_local_order
        :param local_ref:
        :param insert_args:
        """
        if insert_args.is_buy():
            insert_args.price = SysWidget.get_tick_data().get(insert_args.instrument).BidPrice
        else:
            insert_args.price = SysWidget.get_tick_data().get(insert_args.instrument).AskPrice
        insert_args.is_local = True
        self._insert_local_traded_order(local_ref, insert_args)
        Sys.time_profile_end(insert_args.strategy_name, insert_args.name, 'ThriftCline')

    def insert_order(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> None
        """
        :param local_ref:
        :param insert_args:
        :return:
        """
        Sys.time_profile_init(insert_args.strategy_name, insert_args.name, 'ThriftCline')
        if self.__is_local:
            SleepCommand(0.5, Command(target=self.insert_analog_order, args=(local_ref, insert_args)),
                         SysWidget.get_main_engine())
            return

        if Sys.AnalogTradeClient or insert_args.is_local:
            self._insert_local_traded_order(local_ref, insert_args)
        else:
            self._insert_remote_order(local_ref, insert_args)
        Sys.time_profile_end(insert_args.strategy_name, insert_args.name, 'ThriftCline')

    def _try_restart_and_failed_cancel(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> bool
        if not self.restart():
            RtnMsgMaker.send_rtn_order_canceled_event(local_ref, 0, insert_args.volume)
            self.__restarted = False
            self.__logger.ERR('try restart false')
            return False
        return True

    def _insert_remote_order(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> None
        try:
            Sys.time_profile(insert_args.strategy_name, insert_args.name, 'ThriftCline', 'remote')
            self.__logger.INFO(insert_args.strategy_name, 'remote_order_insert:%s', str(insert_args))
            self.__client.ReqOrderInsert(insert_args.instrument, insert_args.price,
                                         ord(insert_args.offset),
                                         ord(insert_args.trade_side), insert_args.volume,
                                         ord(insert_args.order_price_type),
                                         ord(insert_args.time_condition),
                                         ord(insert_args.contingent_condition), int(local_ref))
            self.__restarted = False

            if insert_args.time_out != 0:
                OrderTimeOutCheckCommand(insert_args.time_out, local_ref, self)
            self.__logger.INFO(insert_args.strategy_name,
                               'ReqOrderInsert:res - _local_ref:%s' % local_ref)
        except Exception as e:
            self.__logger.INFO(msg='try to restart with err:%s' % str(e))
            if not self._try_restart_and_failed_cancel(local_ref, insert_args):
                return
            self._insert_remote_order(local_ref, insert_args)
            return

    def _insert_local_traded_order(self, local_ref, insert_args):
        # type: (str, InsertArgs) -> None
        Sys.time_profile(insert_args.strategy_name, insert_args.name, 'ThriftCline', 'local')
        self.__logger.INFO(insert_args.strategy_name,
                           'ReqOrderInsert:res - local_order - OrderRef:%s' % local_ref)
        RtnMsgMaker.send_rtn_trade_event(insert_args.strategy_name, local_ref, RtnMsgMaker.next_id(), insert_args)
        RtnMsgMaker.send_rtn_order_event(insert_args.strategy_name, local_ref, OnRtnOrderState.FILLED,
                                         insert_args.volume, insert_args.volume)

    def canceled(self, local_ref):
        # type: (str) -> None
        """
        :param local_ref:
        """
        strategy_name = self.__ref_mapper.get_strategy_name(local_ref)
        instrument = self.__ref_mapper.get_instrument(local_ref)
        self.__logger.INFO(strategy_name, 'canceled - instrument:%s _local_ref:%s]', instrument, local_ref)
        self.__client.ReqOrderAction(instrument, int(local_ref), ord('0'))

    def req_qry_investor_position_detail(self, name, instrument=''):
        # type: (str, str) -> None
        """
        :param name:
        :param instrument:
        """
        self.__logger.INFO(msg='ReqQryInvestorPositionDetail(%s)' % instrument)
        self.__client.ReqQryInvestorPositionDetail(instrument or '')

    def req_qry_order(self, name, instrument, order_sys_id, insert_time_start, insert_time_end):
        # type: (str, str, str, str, str) -> None
        """
        :param name:
        :param instrument:
        :param order_sys_id:
        :param insert_time_start:
        :param insert_time_end:
        """
        self.__logger.INFO(
            msg='ReqQryOrder(%s, %s, %s, %s)' % (instrument, order_sys_id, insert_time_start, insert_time_end))
        self.__client.ReqQryOrder(instrument, order_sys_id, insert_time_start, insert_time_end)

    def req_qry_trading_account(self, name):
        # type: (str) -> None
        """
        :param name:
        """
        try:
            self.__client.ReqQryTradingAccount()
            self.__restarted = False
        except Exception as e:
            self.__logger.INFO(msg='try to restart:' + str(e))
            if self.restart():
                self.req_qry_trading_account(name)

    def on_rtn_position_detail(self, position_detail_dict, rsq_info_dict, rsp_id, is_last):
        if rsq_info_dict.get('ErrorID', 0) != 0:
            self.__logger.ERR('RtnPositionDetail:{}'.format(rsq_info_dict.get('ErrorMsg').decode('gb2312').encode('utf8')))
        else:
            d = position_detail_dict
            direction = chr(d['Direction'])
            ins = d['InstrumentID']
            if self.__temp.get(rsp_id) is None:
                self.__temp[rsp_id] = {'0':{}, '1':{}}
            p = self.__temp[rsp_id]
            p[direction][ins] = p[direction].get(ins, 0) + d['Volume']
            if is_last:
                self.__on_rtn_position_event.emit(p)
                del self.__temp[rsp_id]

    def subscribe_rtn_account(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_account_event.subscribe(func)

    def unsubscribe_rtn_account(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_account_event.unsubscribe(func)

    def subscribe_rtn_order(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_order_event.subscribe(func)

    def subscribe_rtn_trade(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_trade_event.subscribe(func)

    def unsubscribe_rtn_order(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_order_event.unsubscribe(func)

    def unsubscribe_rtn_trade(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_trade_event.unsubscribe(func)

    def subscribe_rtn_position(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_position_event.subscribe(func)

    def unsubscribe_rtn_position(self, func):
        # type: (callable) -> None
        """
        :param func:
        """
        self.__on_rtn_position_event.unsubscribe(func)

    def __restart_command(self):
        # type: () -> None
        if self.__client is not None:
            self.restart()

    def __set_restart_command(self):
        # type: () -> None
        cmd = Command(target=self.__restart_command, name='CTPTradeClinetRestart')
        IntervalDateTimeCommand(datetime.time(20, 50), cmd, factory.object_engine)
        IntervalDateTimeCommand(datetime.time(8, 50), cmd, factory.object_engine)
