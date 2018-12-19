import abc


class BaseSender(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def send(self, *args, **kwargs):
        raise NotImplementedError
