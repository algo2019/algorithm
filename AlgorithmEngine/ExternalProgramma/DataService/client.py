import ds_tools
ds_tools.instead_json()

import config
import jrpc

__all__ = ['Client']


class Client(object):
    def __init__(self):
        self._client = jrpc.service.SocketProxy(config.Port, config.Host, timeout=None)

    def __del__(self):
        self._client.close()

    def tdays(self, start, end=None):
        return self._client.tdays(start, end)

    def tdaysoffset(self, offset, dt=None):
        return self._client.tdaysoffset(offset, dt)

    def main_contract(self, symbol, start, end):
        return self._client.main_contract(symbol, start, end)

    def day(self, code, start, end, fields='openprice,highprice,lowprice,closeprice,volume'):
        return self._client.day(code, start, end, fields)

    def is_trading_day(self, dt=None):
        return self._client.is_trading_day(dt)
