from PubSubAdapter import PubSubAdapter
from Common.Event import Event
from threading import Thread
import redis


class RedisPubSub(PubSubAdapter):
    def __init__(self, host, port):
        self.__redis = redis.StrictRedis(host, port)
        self.__ps = self.__redis.pubsub()
        self.__sub_events = {}
        self.__started = False
        self.__running_exception_handler = None

    def publish(self, key, msg):
        self.__redis.publish(key, msg)

    def subscribe(self, keys, handler):
        if type(keys) != list:
            keys = keys.split('|')
        for key in keys:
            self.__subscribe(key, handler)
        self.__start()

    def __subscribe(self, key, handler):
        if self.__sub_events.get(key) is None:
            self.__sub_events[key] = Event()
            self.__ps.psubscribe(key)
        self.__sub_events[key].subscribe(handler)

    def unsubscribe(self, key, handler):
        self.__sub_events[key].unsubscribe(handler)

    def __run(self):
        try:
            for msg in self.__ps.listen():
                try:
                    if msg['type'] != 'pmessage':
                        continue
                    self.__sub_events[msg['pattern']].emit(msg)
                except Exception as e:
                    if self.__running_exception_handler is not None:
                        self.__running_exception_handler(e)
        finally:
            self.__started = False
            self.__start()

    def set_running_exception_handler(self, handler):
        self.__running_exception_handler = handler

    def __start(self):
        if self.__started:
            return
        self.__started = True
        th = Thread(target=self.__run, name='RedisPubSub')
        th.setDaemon(True)
        th.start()
