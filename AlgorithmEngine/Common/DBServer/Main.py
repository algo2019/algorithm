import time, sys

from Common import PublishLog
from SqliteServer import Server
from Common.PubSubAdapter.RedisPubSub import RedisPubSub
from Common.ExternalCommand import get_executor
from Common.AtTimeObjectEngine import ThreadEngine
import Conf
import DBHandler

DB = Server(Conf.DB_PATH)
sys.modules[Conf.DB_MODULE] = DB

ENGINE = ThreadEngine('DBServerEngine')

PS = RedisPubSub(Conf.REDIS_HOST, Conf.REDIS_PORT)

LOGGER = PublishLog.Logger('DBServer', PS, ENGINE)

LOG_PS_KEY = PublishLog.get_monitor_key(Conf.LOG_NAME)
EXTERNAL_EXECUTOR = get_executor(PS, Conf.PS_KEY, ENGINE)
DBHandler.register()

setattr(DB, 'keep_running', 1)
setattr(DB, 'logger', LOGGER)


def publish_err(*args):
    import traceback
    LOGGER.ERR(LOG_PS_KEY, traceback.format_exc())

ENGINE.set_running_exception_handler(publish_err)
PS.set_running_exception_handler(publish_err)

DB.open()
EXTERNAL_EXECUTOR.start()

LOGGER.INFO(LOG_PS_KEY, 'DBServer started')

ENGINE._started = True
ENGINE.run()
