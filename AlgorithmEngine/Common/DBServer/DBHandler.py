import sys

import Conf

DB = None
from Common.ExternalCommand.Executor import Handler


def table_call(tid, name, item, args, kwargs):
    try:
        return getattr(DB.Tables[name], item)(*args, **kwargs)
    except:
        import traceback
        Handler.send_err(tid, traceback.format_exc())


def table_register(tid, codes):
    table_instance = None
    codes += codes + '\ntable_instance = create()\nimport Conf\nDB = sys.modules[Conf.DB_MODULE]\nDB.Tables[table_instance.name] = table_instance'
    try:
        exec codes
    except:
        import traceback
        Handler.send_err(tid, traceback.format_exc())


def register():
    global DB
    DB = sys.modules[Conf.DB_MODULE]
    if not hasattr(DB, 'Tables'):
        setattr(DB, 'Tables', {})

    Handler.subscribe(Conf.TABLE_CALL_CMD, table_call)
    Handler.subscribe(Conf.TABLE_REGISTER_CMD, table_register)
