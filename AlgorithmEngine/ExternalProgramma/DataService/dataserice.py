import ds_tools
ds_tools.instead_json()

import jrpc
from Common.Dao.DBDataDao import DBDataDao
import config


__all__ = ['DataService', 'start']


class DataService(jrpc.service.SocketObject):
    def __init__(self):
        super(DataService, self).__init__(config.Port, config.Host)
        self._dao = DBDataDao()

    @jrpc.service.method
    def tdays(self, *args, **kwargs):
        return self._dao.tdays(*args, **kwargs)

    @jrpc.service.method
    def tdaysoffset(self, *args, **kwargs):
        return self._dao.tdaysoffset(*args, **kwargs)

    @jrpc.service.method
    def main_contract(self, *args, **kwargs):
        return self._dao.main_contract(*args, **kwargs)

    @jrpc.service.method
    def day(self, *args, **kwargs):
        return self._dao.day(*args, **kwargs)

    @jrpc.service.method
    def is_trading_day(self, *args, **kwargs):
        return self._dao.is_trading_day(*args, **kwargs)


def start():
    server = DataService()
    server.run_wait()


if __name__ == '__main__':
    start()