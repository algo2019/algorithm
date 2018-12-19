# -*- coding: utf-8 -*-
from ThostFtdcUserApiStruct cimport *
from libcpp.string cimport string
from libcpp cimport bool
from Python cimport *
import abc


cdef extern from "server.h":
    ctypedef void (*handler_ptr)(void *)

    cdef cppclass TradeService:
        TradeService(string& broker_id, string& investor_id, string& password, string& front_trade_address,
                     string& redis_address, int redis_port, string& publish_key)
        void ReqOrderInsert(string& instrument, double price, char offset_flag, char direction, int volume,
                            char order_price_type, char time_condition, char contingent_condition, int local_ref) except *
        void ReqOrderAction(string& instrument, int local_ref, char action_flag) except *
        int ReqQryInvestorPositionDetail(string& instrument) except *
        int ReqQryTradingAccount() except *
        void ReqQryOrder(string& instrument, string& order_sys_id, string& insert_time_start, string& insert_time_end) except *
        void ReqQryTrade() except *
        void SubscribeOnRtnOrder(handler_ptr handler) except *
        void SubscribeOnRtnTrade(handler_ptr handler) except *
        void SetOnRspQryTradingAccountHandler(void (*)(CThostFtdcTradingAccountField *, CThostFtdcRspInfoField *, int, bint)) except *
        void SetOnRspQryInvestorPositionDetailHandler(void (*)(CThostFtdcInvestorPositionDetailField *, CThostFtdcRspInfoField *, int , bint)) except *

cdef object _TradeService = None

cdef void on_rtn_trade(void *rt_trade):
    cdef PyGILState_STATE state = PyGILState_Ensure()
    if _TradeService is not None:
        _TradeService.OnRtnTrade((<CThostFtdcTradeField *>rt_trade)[0])
    PyGILState_Release(state)

cdef void on_rtn_order(void *rt_order):
    cdef PyGILState_STATE state = PyGILState_Ensure()
    if _TradeService is not None:
        _TradeService.OnRtnOrder((<CThostFtdcOrderField *>rt_order)[0])
    PyGILState_Release(state)

cdef void on_rtn_trade_account(CThostFtdcTradingAccountField * trading_account, CThostFtdcRspInfoField * rsq_info, int rsq_id, bool is_last):
    cdef PyGILState_STATE state = PyGILState_Ensure()
    trading_account_dict = {} if <void*>trading_account == <void*>0 else trading_account[0]
    rsq_info_dict = {} if  <void*>rsq_info == <void*>0 else rsq_info[0]
    if _TradeService is not None:
        _TradeService.OnRtnTradingAccount(trading_account_dict, rsq_info_dict, rsq_id, is_last)
    PyGILState_Release(state)


cdef void on_rtn_position_detail(CThostFtdcInvestorPositionDetailField *position_detail, CThostFtdcRspInfoField *rsp_info, int rsp_id, bool is_last):
    cdef PyGILState_STATE state = PyGILState_Ensure()
    position_detail_dict = {} if <void*>position_detail == <void*>0 else position_detail[0]
    rsq_info_dict = {} if <void*>rsp_info == <void*>0 else rsp_info[0]
    if _TradeService is not None:
        _TradeService.OnRtnPositionDetail(position_detail_dict, rsq_info_dict, rsp_id, is_last)
    PyGILState_Release(state)


cpdef init_thread():
    PyEval_InitThreads()


def init_thread2():
    import threading
    threading.Thread(target=str, args=(1, )).start()


class TradeServiceSpi(object):
    """
    回调类，通过PyTradeService.RegisterSpi注册
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def on_rtn_order(self, dict rtn_order):
        raise NotImplementedError

    @abc.abstractmethod
    def on_rtn_trade(self, dict rtn_trade):
        raise NotImplementedError

    @abc.abstractmethod
    def on_rtn_trade_account(self, dict trade_account, dict rsp_info, int rsp_id, bint is_last):
        raise NotImplementedError

    @abc.abstractmethod
    def on_rtn_position_detail(self, dict position_detail_dict, dict rsq_info_dict, int rsp_id, bint is_last):
        raise NotImplementedError


cdef class PyTradeService:
    """
    需要先调用RegisterSpi在调用start
    """

    cdef TradeService * ptr
    cdef object spi

    def __cinit__(self):
        global _TradeService
        if _TradeService is not None:
            raise Exception('PyTradeService just allow one instance')
        _TradeService = self
        self.spi = None

    def start(self, string& broker_id, string& investor_id, string& password, string& front_trade_address,
                     string& redis_address, int redis_port, string& publish_key):
        if self.spi is None:
            raise Exception('RegisterSpi should be called!')
        self.ptr = new TradeService(broker_id, investor_id, password, front_trade_address, redis_address,
                                    redis_port, publish_key)
        self.ptr.SubscribeOnRtnOrder(on_rtn_order)
        self.ptr.SubscribeOnRtnTrade(on_rtn_trade)
        self.ptr.SetOnRspQryTradingAccountHandler(on_rtn_trade_account)
        self.ptr.SetOnRspQryInvestorPositionDetailHandler(on_rtn_position_detail)

    def __dealloc__(self):
        if self.ptr != NULL:
            del self.ptr
        global _TradeService
        _TradeService = None

    def RegisterSpi(self, object spi):
        # type: (TradeServiceSpi) -> object
        """
        设置回调类，重复调用会覆盖之前
        :param spi:
        """
        self.spi = spi

    def UnRegisterSpi(self):
        self.spi = None

    def ReqOrderInsert(self, str instrument, double price, char offset_flag, char direction, int volume,
                            char order_price_type, char time_condition, char contingent_condition, int local_ref):
        self.ptr.ReqOrderInsert(instrument, price, offset_flag, direction, volume, order_price_type, time_condition,
                                contingent_condition, local_ref)

    def ReqOrderAction(self, str instrument, int local_ref, char action_flag):
        self.ptr.ReqOrderAction(instrument, local_ref, action_flag)

    def ReqQryInvestorPositionDetail(self, str instrument):
        return self.ptr.ReqQryInvestorPositionDetail(instrument)

    def ReqQryTradingAccount(self):
        return self.ptr.ReqQryTradingAccount()

    def ReqQryOrder(self, str instrument, str order_sys_id, str insert_time_start, str insert_time_end):
        self.ptr.ReqQryOrder(instrument, order_sys_id, insert_time_start, insert_time_end)

    def ReqQryTrade(self):
        self.ptr.ReqQryTrade()

    def OnRtnTrade(self, dict rtn_trade):
        if self.spi is not None:
            self.spi.on_rtn_trade(rtn_trade)

    def OnRtnOrder(self, dict rtn_order):
        if self.spi is not None:
            self.spi.on_rtn_order(rtn_order)

    def OnRtnTradingAccount(self, dict trade_account, dict rsp_info, int rsq_id, bint is_last):
        if self.spi is not None:
            self.spi.on_rtn_trade_account(trade_account, rsp_info, rsq_id, is_last)

    def OnRtnPositionDetail(self, dict position_detail_dict, dict rsq_info_dict, int rsp_id, bint is_last):
        if self.spi is not None:
            self.spi.on_rtn_position_detail(position_detail_dict, rsq_info_dict, rsp_id, is_last)
