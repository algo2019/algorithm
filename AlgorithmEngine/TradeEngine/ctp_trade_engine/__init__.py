# -*- coding: utf-8 -*-
"""
__init__.py
"""
from .tradeclientfactory import factory, Config as CTPTradeEngineConfig
from .insertargs import InsertArgs

__all__ = ['CTPTradeEngine', 'TradeClientConfig', 'InsertArgs']


def CTPTradeEngine():
    # type: () -> factory.trade_client
    """
    The singleton pattern
    :return:
    """
    return factory.trade_client
