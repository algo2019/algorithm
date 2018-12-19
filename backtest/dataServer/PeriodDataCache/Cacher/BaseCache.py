import abc


class Cacher(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_data(self, conf):
        raise NotImplementedError()

    @abc.abstractmethod
    def cache_data(self, conf, data):
        raise NotImplementedError()
