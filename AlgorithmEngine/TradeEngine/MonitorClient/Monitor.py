import datetime
import threading
import time
import traceback

from Common.CommonLogServer.RedisLogService import PublishLogCommand
from Common.Event import Event
from TradeEngine.GlobleConf import Sys, SysWidget, StartConf
from TradeEngine.GlobleConf.RedisKey import Publish


class CheckFunc(object):
    def __init__(self, name, func=None, msg='', strategy=None, *args, **kwargs):
        if not func:
            self.__func = self.default()
        else:
            self.__func = func
        if strategy is not None:
            self.__logger = get_server_log(name)
        else:
            self.__logger = get_logger(name)
        self.__strategy_name = strategy
        self.__args = args
        self.__kwargs = kwargs
        self.__name = name
        self.__msg = msg

    def setFunc(self, func, *args, **kwargs):
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    def default(self):
        return True

    def check(self):
        if not self.__func(*self.__args, **self.__kwargs):
            self.err()
        else:
            self.info()

    @property
    def name(self):
        return self.__name

    @property
    def logger(self):
        return self.__logger

    @property
    def msg(self):
        return self.__msg

    @msg.setter
    def msg(self, msg):
        self.__msg = msg

    def err(self, msg=None):
        if not msg:
            msg = self.msg
        if self.__strategy_name is None:
            self.logger.ERR(msg)
        else:
            self.logger.ERR(self.__strategy_name, msg)

    def info(self):
        pass


class Thread(CheckFunc, threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, repeat=True,
                 strategy=None):
        CheckFunc.__init__(self, name=name, func=self.isAlive, strategy=strategy)
        threading.Thread.__init__(self, group, None, name, None, None, verbose)
        self.__args = args
        if kwargs is None:
            self.__kwargs = {}
        else:
            self.__kwargs = kwargs
        self.__target = target
        self.__repeat = repeat
        self.setDaemon(True)
        self.msg = 'is not Alive'
        if get_monitor():
            Monitor.create().addCheck(self)
        self.__stoped = False
        self.__condition = threading.Condition()

    def run(self, *args, **kwargs):
        while 1:
            try:
                if self.__target:
                    self.__target(*self.__args, **self.__kwargs)
                else:
                    self._run()
            except Exception:
                self.msg = traceback.format_exc()
                print self.msg
                self.err()
            if not self.__repeat:
                return

    def _run(self):
        pass

    def stop(self):
        self.__stoped = True
        self.err('Thread:Stoped')

    def restart(self):
        if self.__stoped:
            self.__stoped = False
            self.__condition.acquire()
            self.__condition.notify_all()
            self.__condition.release()
            self.err('Thread:Restart')

    @property
    def stoped(self):
        return self.__stoped


class HeartBeatThread(Thread):
    def __init__(self, heartBeatPeriod):
        Thread.__init__(self, name='Monitor.heartBeat')
        self.__level = 'HEARTBEAT'
        self.__delay = heartBeatPeriod
        self.__checkEvent = None
        self.__checkStarted = False
        self.__heartBeatStarted = False
        self.__heart_beat_key = None
        self.setDaemon(True)

    def startHeartBeat(self, strategy):
        self.__heartBeatStarted = True
        self.__heart_beat_key = Publish.HeartBeat(strategy)

    def startCheck(self, checkEvent):
        self.__checkEvent = checkEvent
        self.__checkStarted = True

    def _run(self):
        while not self.stoped:
            time.sleep(self.__delay)
            if self.__heartBeatStarted:
                SysWidget.get_redis_reader().publish(self.__heart_beat_key, str(time.time()))
            if self.__checkStarted:
                self.__checkEvent.emit()


class Monitor(object):
    def __init__(self, strategy_name, heartBeatPeriod=1):
        self.__strategy_name = strategy_name
        self.__heartThread = HeartBeatThread(heartBeatPeriod)
        self.__heartThread.start()
        self.__checkEvent = Event()

    @property
    def strategy_name(self):
        return self.__strategy_name

    def startHeartBeat(self):
        self.__heartThread.startHeartBeat(self.__strategy_name)

    def startCheck(self):
        self.__heartThread.startCheck(self.__checkEvent)

    def stopHearBeat(self):
        self.__heartThread.stop()
        self.__heartThread = None

    def addCheck(self, checkObject):
        self.__checkEvent.subscribe(checkObject.check)

    def removeCheck(self, checkObject):
        self.__checkEvent.unsubscribe(checkObject.check)

    __SINGLETON = None

    @classmethod
    def create(cls, uniqueName=None):
        if not cls.__SINGLETON:
            if not uniqueName:
                return None
            else:
                cls.__SINGLETON = cls(uniqueName)
        return cls.__SINGLETON


class DefaultLogger(object):
    def __init__(self):
        pass

    @property
    def key(self):
        return 'None'

    def addCheck(self, *args):
        pass

    def publish(self, level, source, msg, args, keys='None'):
        if len(args):
            msg = msg % args
        print '[%s] [%s] [%s] [%s] [%s]' % (keys, str(datetime.datetime.now()), level, source, msg)


def get_monitor(unique_name=None):
    return Monitor.create(unique_name)


class Logger(object):
    def __init__(self, source, strategy_name=None):
        self.__source = source
        from TradeEngine.MonitorService.ServerEngine import Engine
        self.__engine = Engine
        self.__strategy = strategy_name

    @property
    def strategy(self):
        if self.__strategy is None:
            self.__strategy = get_monitor().strategy_name
        return self.__strategy

    def publish(self, level, msg, args=tuple()):
        self.__engine.add_command(PublishLogCommand(StartConf.PublishKey, 'publish', self.__strategy, level,
                                                    self.__source, msg, args))


    def INFO(self, msg, *args):
        self.publish('INFO', msg, args)

    def ERR(self, msg, *args):
        self.publish('ERR', '@%s@' % msg, args)

    def WARN(self, msg, *args):
        self.publish('WARN', msg, args)

    def DEBUG(self, msg, *args):
        self.publish('DEBUG', msg, args)


class ServerLogger(object):
    def __init__(self, source):
        self.__source = source
        from TradeEngine.GlobleConf import SysWidget
        self.__engine = SysWidget.get_log_engine()

    def publish(self, level, msg, args=tuple(), strategy_name=None):
        if strategy_name is None:
            strategy_name = Sys.ServerApp
        self.__engine.add_command(PublishLogCommand(StartConf.PublishKey, 'publish', strategy_name, level,
                                                    self.__source, msg, args))

    def INFO(self, strategy_name=None, msg='', *args):
        self.publish('INFO', msg, args, strategy_name)

    def ERR(self, strategy_name=None, msg='', *args):
        self.publish('ERR', '@%s@' % msg, args, strategy_name)

    def WARN(self, strategy_name=None, msg='', *args):
        self.publish('WARN', msg, args, strategy_name)

    def DEBUG(self, strategy_name=None, msg='', *args):
        self.publish('DEBUG', msg, args, strategy_name)


__LOGGERS = {}


def get_logger(source, strategy=None):
    if __LOGGERS.get(source) is None:
        __LOGGERS[source] = Logger(source, strategy)
    return __LOGGERS[source]


__SERVER_LOGGERS = {}


def get_server_log(source):
    if __SERVER_LOGGERS.get(source) is None:
        __SERVER_LOGGERS[source] = ServerLogger(source)
    return __SERVER_LOGGERS[source]
