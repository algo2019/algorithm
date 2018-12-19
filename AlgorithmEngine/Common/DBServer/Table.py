import sys
from Common.DBServer import Conf
import BaseTable

__SERVER__ = 0
__CLIENT__ = 1
if sys.modules.get(Conf.DB_MODULE) is None:
    __SYS__ = __CLIENT__
    from Common.PubSubAdapter.RedisPubSub import RedisPubSub
    from Common.ExternalCommand import get_caller

    PK = Conf.PS_KEY
    PS = RedisPubSub(Conf.REDIS_HOST, Conf.REDIS_PORT)
    CALLER = get_caller(PS, PK)
else:
    __SYS__ = __SERVER__
    DB = sys.modules.get(Conf.DB_MODULE)


def is_server():
    return __SYS__ == __SERVER__


class Table(BaseTable.Table):
    def __init__(self, name):
        self._local_attr = {'name', 'get_db'}
        self.__f_register = False
        super(Table, self).__init__(name)

    def get_db(self):
        if is_server():
            return __import__(Conf.DB_MODULE)
        else:
            return None

    def __getattribute__(self, item):
        if __SYS__ == __CLIENT__:
            if item == '_local_attr' or item in self._local_attr:
                return super(Table, self).__getattribute__(item)

            that = self

            def rt(*args, **kwargs):
                return CALLER.call(Conf.TABLE_CALL_CMD,
                                   (that.name, item, args, kwargs))

            return rt
        elif __SYS__ == __SERVER__:
            return super(Table, self).__getattribute__(item)
        else:
            raise Exception('Unknown __SYS__ %s' % str(__SYS__))


def register_to_db(table_module):
    path = table_module.__file__
    if path.endswith('.pyc'):
        path = path[:-1]
    elif not path.endswith('.py'):
        raise Exception('Table Module need python code')
    with open(path, 'r') as f:
        CALLER.call(Conf.TABLE_REGISTER_CMD, (f.read(),))


def register_local_table(table_module):
    table = table_module.create()
    DB.Tables[table.name] = table
    table.__getattribute__ = lambda x: super(Table, table).__getattribute__(x)
    return table
