import json
import threading
from Common.PubSubAdapter.RedisPubSub import RedisPubSub
import time
import sys


class RedisBridge(object):
    def __init__(self, s, d, key):
        self.__sr = s
        self.__dr = d
        self.__keys = key
        self.__started = False
        self.__ps = None

    def start(self):
        if not self.__started:
            self.__started = True
            t = threading.Thread(target=self.__start)
            t.setDaemon(True)
            t.start()

    def __start(self):
        self.__ps = self.__sr.pubsub()
        self.__ps.psubscribe(self.__keys)
        for msg in self.__ps.listen():
            if msg['type'] != 'pmessage':
                continue
            if not self.__started:
                break
            self.__dr.publish(msg['channel'], msg['data'])

    def stop(self):
        if self.__started:
            self.__started = False
            if self.__ps is not None:
                self.__ps.punsubscribe(self.__keys)


class Translator(object):
    def __init__(self, s, d, key):
        self._s = s
        self._d = d
        self._key = key
        self._last_update = 0
        self._translating_stop = threading.Event()
        self._translating_stop.set()
        self._counter = {}

    def start(self):
        self._s.subscribe(self._key, self._check_translate_stop_s)
        self._s.subscribe(self._key, self._translate)
        self._d.subscribe(self._key, self._update_key)
        self._d.subscribe(self._key, self._check_translate_stop_d)

        ts = [
            threading.Thread(target=self._check_key),
        ]
        map(lambda t: t.setDaemon(True), ts)
        map(lambda t: t.start(), ts)

    def _check_translate_stop_s(self, msg):
        if self._translating_stop.is_set():
            return
        if self._counter.get(msg['channel']) is None:
            self._counter[msg['channel']] = 1
        else:
            self._counter[msg['channel']] += 1

    def _check_translate_stop_d(self, msg):
        if self._translating_stop.is_set():
            return
        if self._counter.get(msg['channel']) is None:
            self._counter[msg['channel']] = 0
        else:
            if self._counter[msg['channel']] == 0:
                self._translating_stop.set()
                self._counter = {}
            else:
                self._counter[msg['channel']] -= 1

    def _translate(self, msg):
        if self._translating_stop.is_set():
            return
        self._d.publish(msg['channel'], msg['data'])

    def _start_translate(self):
        self._translating_stop.clear()
        self._translating_stop.wait()

    def _check_key(self):
        while 1:
            time.sleep(1)
            if time.time() - self._last_update > 2:
                self._start_translate()

    def _update_key(self, msg):
        self._last_update = time.time()


def main(config_file, wait=True):
    with open(config_file, 'r') as f:
        config = json.load(f)
    m = None
    b = None
    for market in config['market']:
        if market['name'] == 'Main':
            m = market
        elif market['name'] == 'Back':
            b = market
    if not (m and b):
        raise Exception('Main and Back is need!')

    print 'Main', m['host'], m['port']
    print 'Back', b['host'], b['port']
    rm = RedisPubSub(m['host'], m['port'])
    rb = RedisPubSub(b['host'], b['port'])
    for item in m['item']:
        if item.get('translate'):
            print 'Translate', item['key']
            Translator(rb, rm, item['key']).start()
    while wait:
        time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("need a json config file")
    main(sys.argv[1])
