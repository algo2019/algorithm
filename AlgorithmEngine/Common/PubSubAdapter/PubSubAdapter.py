import abc


class PubSubAdapter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def publish(self, key, msg):
        raise NotImplementedError

    @abc.abstractmethod
    def subscribe(self, key, handler):
        raise NotImplementedError

    @abc.abstractmethod
    def unsubscribe(self, key, handler):
        raise NotImplementedError

    @abc.abstractmethod
    def set_running_exception_handler(self, handler):
        raise NotImplementedError
