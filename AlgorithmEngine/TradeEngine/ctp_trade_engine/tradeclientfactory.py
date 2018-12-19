# -*- coding: utf-8 -*-
"""
ctp_trade_engine.factory
"""

__all__ = ['Config', 'factory']


class Config(object):
    """
    ctp_trade_engine.Config
    """
    ctp_trade_host = None
    broker_id = None
    user_id = None
    password = None
    publish_key = None
    redis_host = None
    redis_port = None
    is_local = False
    market_point = 10

    @classmethod
    def set(cls, ctp_trade_host, broker_id, user_id, password, publish_key, redis_host, redis_port, is_local=False):
        # type: (str, str, str, str, str, str, int, bool) -> None
        """
        :param ctp_trade_host:
        :param broker_id:
        :param user_id:
        :param password:
        :param publish_key:
        :param redis_host:
        :param redis_port:
        :param is_local:
        """
        (cls.ctp_trade_host, cls.broker_id, cls.user_id, cls.password, cls.publish_key,
         cls.redis_host, cls.redis_port, cls.is_local) = (
            ctp_trade_host, broker_id, user_id, password, publish_key, redis_host, redis_port, is_local)

    @classmethod
    def as_args(cls):
        # type: () -> tuple
        """
        :return: a tuple as CTPTradeClient's params
        """
        rt = (cls.ctp_trade_host, cls.broker_id, cls.user_id, cls.password, cls.publish_key,
              cls.redis_host, cls.redis_port, cls.is_local)
        if None in rt:
            raise Exception('ctp_trade_engine.Config Has None:{}'.format(str(rt)))
        return rt


class _Factory(object):
    __temp = {}

    @property
    def ctp_trade_client(self):
        # type: () -> CTPTradeClient
        """
        :return:
        """
        if self.__temp.get('CTPTradeClient') is None:
            from .ctptradeclinet import CTPTradeClient
            if Config.publish_key.startswith('ANALOG'):
                Config.is_local = True
            self.__temp['CTPTradeClient'] = CTPTradeClient(*Config.as_args())
            try:
                self.__temp['CTPTradeClient'].start()
            except:
                from TradeEngine.GlobleConf import Sys
                if Sys.Debug:
                    import sys
                    sys.stderr.write('factory: ctp_trade_engine start failed\n')
                else:
                    raise
        return self.__temp['CTPTradeClient']

    @property
    def object_engine(self):
        # type: () -> object
        """
        :return:
        """
        if self.__temp.get('ObjectEngine') is None:
            from TradeEngine.GlobleConf import SysWidget
            self.__temp['ObjectEngine'] = SysWidget.get_main_engine()
        return self.__temp['ObjectEngine']

    @property
    def close_trade_client(self):
        # type: () -> CloseTradeClient
        """
        :return:
        """
        if self.__temp.get('CloseTradeClient') is None:
            from .closetradeclient import CloseTradeClient
            self.__temp['CloseTradeClient'] = CloseTradeClient(self.ctp_trade_client)
        return self.__temp['CloseTradeClient']

    @staticmethod
    def service_logger(source):
        # type: (str) -> MyServerLogger
        """
        :return:
        """
        from TradeEngine.GlobleConf.mlogging import MyServerLogger
        from TradeEngine.GlobleConf import SysWidget
        return SysWidget.get_service_logger(source)

    @property
    def trade_client(self):
        # type: () -> TradeClient
        """
        :return:
        """
        if self.__temp.get('ctp_trade_engine') is None:
            from .tradeclient import TradeClient
            self.__temp['ctp_trade_engine'] = TradeClient()
        return self.__temp['ctp_trade_engine']

    @property
    def order_insert_checker(self):
        # type: () -> module
        """
        :return:
        """
        from . import orderinsertcheckconfig
        # noinspection PyTypeChecker
        return orderinsertcheckconfig

    @property
    def ctptradeengineso(self):
        # type: () -> module
        # noinspection PyUnresolvedReferences
        try:
            from pylib import ctptradeengine
            return ctptradeengine
        except:
            from TradeEngine.GlobleConf import Sys
            if Sys.Debug:
                import sys
                sys.stderr.write('factory: ctptradeengineso is disable\n')

                class ctptradeengine(object):
                    TradeServiceSpi = object

                return ctptradeengine
            else:
                raise


factory = _Factory()
