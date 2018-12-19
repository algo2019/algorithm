import abc


class RemoteAccountWriter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, cache_dice):
        raise NotImplementedError()

    @abc.abstractmethod
    def read(self):
        raise NotImplementedError()
