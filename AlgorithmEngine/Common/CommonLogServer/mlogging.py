# coding=utf-8
import logging
from logging.handlers import HTTPHandler
import Conf as _Conf


class Conf(object):
    HTTP_HOST = '10.4.37.198:5109'
    API_VERSION = _Conf.API_VERSION
    SYS_NAME = 'temp'
    DEBUG = False
    POST_WEB = _Conf.POST_WEB


class RequestFilter(logging.Filter):
    def __init__(self, name):
        super(RequestFilter, self).__init__(name)

    def filter(self, record):
        record.message = record.getMessage()
        return True


LOGGERS = {}


def get_logger(name, sys_name=None):
    if Conf.DEBUG:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(name)s %(filename)s(%(lineno)d)(%(module)s) [%(levelname)s] %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        return logger
    else:
        if LOGGERS.get((name, sys_name)) is None:
            logger = logging.getLogger(name)
            post_url = '{}/api/{}/{}'.format(Conf.POST_WEB, Conf.API_VERSION, sys_name or Conf.SYS_NAME)
            handler = HTTPHandler(Conf.HTTP_HOST, post_url, 'POST')
            logger.addFilter(RequestFilter(name))
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            LOGGERS[(name, sys_name)] = logger
        return LOGGERS[(name, sys_name)]


if __name__ == '__main__':
    Conf.HTTP_HOST = '127.0.0.1:5000'
    get_logger('logging.test').info('enenennen %s', 'aiyou')
