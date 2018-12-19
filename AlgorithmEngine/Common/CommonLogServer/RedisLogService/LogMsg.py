# coding=utf-8
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

import json

import tools
from LogFile import LogFile
from Common.Command import BaseCommand
from Common.CommonLogServer import Conf


class MonitorMsg(BaseCommand):
    def __init__(self, monitor_server, pk, name, data):
        self.__data = data
        self.__name = name
        self.__pk = pk
        self.__monitor_server = monitor_server

    @property
    def monitor_server(self):
        return self.__monitor_server

    @property
    def date_time(self):
        return tools.format_to_datetime(self.__data['datetime'])

    @property
    def name(self):
        return self.__name

    @property
    def source(self):
        return self.__data['source']

    @property
    def level(self):
        return self.__data['level']

    @property
    def tags(self):
        return self.__data.get('tags', 0x0)

    @property
    def data(self):
        return self.__data

    @property
    def msg(self):
        return self.__data['msg']

    @property
    def publish_key(self):
        return self.__pk

    @property
    def show_msg(self):
        return '[{}] [{}] [{}] [{}]'.format(*map(str, (self.date_time, self.level, self.source, self.msg)))

    def execute(self):
        pass


class FileMsg(MonitorMsg):
    def __init__(self, monitor_server, pk, name, data):
        super(FileMsg, self).__init__(monitor_server, pk, name, data)
        self.__file = LogFile()

    def get_file(self, pk, level, name):
        return self.__file.get_file(pk, level, name)

    def execute(self):
        if self.tags | Conf.tags_start == self.tags:
            self.monitor_server.redis.delete(Conf.get_key(self.publish_key, self.name))

        log_file = self.get_file(self.publish_key, self.level, self.name)
        log_file.write(self.show_msg + '\n')
        log_file.flush()


class ErrMsg(FileMsg):
    def __init__(self, monitor_server, pk, name, data):
        super(ErrMsg, self).__init__(monitor_server, pk, name, data)
        self.init_err_sender()

    def init_err_sender(self):
        from Common.ErrSender import ErrMsgSenderMgr, EmailSender, SmsSender
        self.__err_sender = ErrMsgSenderMgr()
        # self.__err_sender.add_sender(SmsSender())
        # self.__err_sender.add_sender(EmailSender())

    def execute(self):
        super(ErrMsg, self).execute()
        key = Conf.get_key(self.publish_key, self.name)
        field = self.source
        value = '[%s] [%s] [%s]' % (self.date_time, self.source, self.msg)
        self.monitor_server.redis.hset(key, field, value)
        err_msg = 'time:{}\nsource:{}.{}\nmsg:{}'.format(
            *map(str, (self.date_time, self.publish_key, self.source, self.msg)))
        self.__err_sender.send(self.publish_key, self.name, err_msg)


LEVEL_CLASS_TABLE = {
    'INFO': FileMsg,
    'ERR': ErrMsg,
    'DEBUG': FileMsg,
    'WARN': FileMsg,
    'HEARTBEAT': MonitorMsg
}


def get_msg(monitor_server, data):
    pk, _, name = data['channel'].split('.')
    try:
        msg_d = json.loads(data['data'])
    except:
        ds = data['data'].split('[')
        msg_d = {
            'datetime': ds[1][:-2],
            'level': ds[2][:-2],
            'source': ds[3][:-2],
            'msg': ds[4][:-1]
        }
    if msg_d['msg'] == 'START':
        msg_d['tags'] = Conf.tags_start

    return LEVEL_CLASS_TABLE.get(msg_d['level'], FileMsg)(monitor_server, pk, name, msg_d)
