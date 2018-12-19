import abc


class Server(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _connect(self):
        raise NotImplementedError

    def open(self):
        self._conn = self._connect()
        self._cursor = self._conn.cursor()

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except:
            pass

    @abc.abstractmethod
    def executemany(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def fetchone(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def fetchall(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self, *args, **kwargs):
        raise NotImplementedError
