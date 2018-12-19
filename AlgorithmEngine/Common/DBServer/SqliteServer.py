import sqlite3
import BaseServer


class Server(BaseServer.Server):
    def __init__(self, path):
        self.__path = path

    def _connect(self):
        return sqlite3.connect(self.__path)

    def execute(self, *args, **kwargs):
        return self._cursor.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self._cursor.executemany(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return self._conn.commit(*args, **kwargs)

    def fetchone(self, *args, **kwargs):
        return self._cursor.fetchone(*args, **kwargs)

    def fetchall(self, *args, **kwargs):
        return self._cursor.fetchall(*args, **kwargs)

    def rollback(self, *args, **kwargs):
        return self._conn.rollback(*args, **kwargs)
