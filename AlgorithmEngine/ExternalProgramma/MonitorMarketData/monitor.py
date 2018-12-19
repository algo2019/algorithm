import datetime
import redis
import json
import abc
import sys
import time
import threading
from ExternalProgramma.DataService import Client
from Common.CommonLogServer.RedisLogService import PublishLogCommand, LocalLogCommand


class CallBack(object):
    @abc.abstractmethod
    def process(self, key):
        raise NotImplemented

    def __call__(self, *args, **kwargs):
        return self.process(*args, **kwargs)


class ErrorProcessor(object):
    @abc.abstractmethod
    def start(self, key):
        raise NotImplemented

    @abc.abstractmethod
    def stop(self, key):
        raise NotImplemented


class RedisChecker(object):
    def __init__(self, host, port, call_back):
        self._redis = redis.StrictRedis(host, port)
        self._items = {}
        self._started = False
        self._call_back = call_back

    def add_item(self, key, period):
        self._items[key] = [0, period]

    def remote_item(self, key):
        self._items.pop(key, None)

    def start(self):
        self._started = True
        t = threading.Thread(target=self._check)
        t.setDaemon(True)
        t.start()
        t2 = threading.Thread(target=self._sub)
        t2.setDaemon(True)
        t2.start()

    def _sub(self):
        ps = self._redis.pubsub()
        ps.psubscribe(*self._items.keys())
        for msg in ps.listen():
            if msg['type'] != 'pmessage':
                continue
            if msg['pattern'] in self._items:
                self._items[msg['pattern']][0] = time.time()

    def _check(self):
        while self._started:
            now = time.time()
            for key in self._items:
                if now - self._items[key][0] > self._items[key][1]:
                    self._call_back(key)
            time.sleep(1)


class MCallBack(CallBack):
    def __init__(self, market):
        self._client = Client()
        self._last_call = {}
        self._market = market

    def process(self, key):
        now = datetime.datetime.now()
        tnow = time.time()
        if datetime.time(14, 59, 30) < now.time() < datetime.time(21, 0, 30):
            pass
        elif datetime.time(2, 29, 30) < now.time() < datetime.time(9, 0, 30):
            pass
        elif datetime.time(10, 14, 30) < now.time() < datetime.time(10, 30, 30):
            pass
        elif datetime.time(11, 29, 30) < now.time() < datetime.time(13, 30, 30):
            pass
        elif tnow - self._last_call.get(key, tnow) < 3:
            pass
        elif datetime.time(9) < now.time() < datetime.time(15):
            if not self._client.is_trading_day():
                pass
            else:
                self.__send_err(key)
        else:
            self.__send_err(key)

        self._last_call[key] = tnow

    def __send_err(self, key):
        if DEBUG:
            log_command = LocalLogCommand
        else:
            log_command = PublishLogCommand
        log_command('Main', 'CheckRedis', 'CheckRedis', 'ERR', 'CheckRedis', '{} {} is out time'.format(
            self._market, key
        )).execute()


def main(config_file, wait=True):
    with open(config_file, 'r') as f:
        config = json.load(f)
    checks = {}
    for market in config['market']:
        print 'market:', market['name'], market['host'], market['port']
        rc = RedisChecker(market['host'], market['port'], MCallBack(market['name']))
        for item in market['item']:
            print 'item:', item['key'], item['period']
            rc.add_item(item['key'], item['period'])
        rc.start()
        checks[market['name']] = rc
    while wait:
        time.sleep(1)

DEBUG = False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("need a json config file")
    main(sys.argv[1])

