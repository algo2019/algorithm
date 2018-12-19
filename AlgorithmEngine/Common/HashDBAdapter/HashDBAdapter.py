import abc


class HashDBAdapter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def hset(self, key, field, value):
        raise NotImplementedError

    @abc.abstractmethod
    def hget(self, key, field):
        raise NotImplementedError

    @abc.abstractmethod
    def hmset(self, key, mapping):
        raise NotImplementedError

    @abc.abstractmethod
    def hgetall(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def keys(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def values(self, key_list):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def hdel(self, key, name):
        raise NotImplementedError

    @abc.abstractmethod
    def type(self, name):
        raise NotImplementedError

    @abc.abstractmethod
    def rename(self, src, dst):
        raise NotImplementedError
