from datetime import *
import time

from NewDataBaseAPI import Adapter as Client


class GTADataBase(object):
    def __init__(self):
        w = Client()
        self.__w = w
        w.start()
        self.tmp = None
        self.call_table = {'tdays': w.tdays, 'tdaysoffset': w.tdaysoffset}
        try:
            self.call_table['wmm'] = w.wmm
        except:
            pass

    def restart(self):
        self.stop()
        time.sleep(10)
        return w.start()

    def stop(self):
        self.__w.stop()

    def data(self, res):
        ds = []
        if not res:
            return ['wmm', []]
        elif type(res) in (list, tuple):
            return ['wmm', res]
        ds.append(res.ErrorCode)
        ds.append(res.Codes)
        ds.append(res.Fields)
        ds.append(res.Times)
        ds.append(res.Data)
        return ds

    def call(self, cmd, arg):
        arg = list(arg)
        res = self.call_table[cmd](*arg)
        return self.data(res)
