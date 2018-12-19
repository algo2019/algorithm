import datetime

from Command import Command


def get_monitor_key(name):
    return 'MONITOR.%s' % name


class Logger(object):

    def __init__(self, source, ps, engine):
        self.__source = source
        self.__ps = ps
        self.__engine = engine

    def timestamp(self):
        return str(datetime.datetime.now())

    def publish(self, key, level, msg, args=tuple()):
            self.__engine.add_command(Command(name='PublishLog', target=self.__execute, args=(key, level, msg, args)))

    def __execute(self, key, level, msg, args):
        if len(args):
            msg = msg % args
        self.__ps.publish(key, '[%s] [%s] [%s] [%s]' % (self.timestamp(), level, self.__source, msg))

    def INFO(self, key, msg, *args):
        self.publish(key, 'INFO', msg, args)

    def ERR(self, key, msg, *args):
        self.publish(key, 'ERR', '@%s@' % msg, args)

    def WARN(self, key, msg, *args):
        self.publish(key, 'WARN', msg, args)

    def DEBUG(self, key, msg, *args):
        self.publish(key, 'DEBUG', msg, args)
