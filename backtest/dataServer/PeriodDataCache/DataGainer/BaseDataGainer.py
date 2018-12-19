import abc


class DataGainer(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_data(self, conf):
        raise NotImplementedError()

