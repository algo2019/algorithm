import socket
import random

from pyalgotrade.optimizer.server import Results

RPC_PATH = '/PyAlgoTradeRPC'

DEFAULT_BATCH_SIZE = 1

DEFAULT_SERVER_PORT = 50000

port_dict = {
    'dt': 50002,
    'ab': 50001,
}


def find_port_by_default(default_port=DEFAULT_SERVER_PORT):
    ret = default_port
    while True:
        try:
            s = socket.socket()
            s.bind(("localhost", ret))
            s.close()
            return ret
        except socket.error:
            pass
        ret = random.randint(1025, 65536)


class JobConfigs(object):
    def __init__(self, strategy_class, instruments_dict, bars_dict, frequency_dict, log_key, result_comparator):
        self.strategy_class = strategy_class
        self.instruments_dict = instruments_dict
        self.bars_dict = bars_dict
        self.frequency_dict = frequency_dict
        self.log_key = log_key
        self.result_comparator = result_comparator


class Job(object):
    def __init__(self, strategyParameters):
        self.__strategyParameters = strategyParameters
        self.__bestResult = None
        self.__bestParameters = None
        self.__id = id(self)

    def getId(self):
        return self.__id

    def getNextParameters(self):
        ret = None
        if len(self.__strategyParameters):
            ret = self.__strategyParameters.pop()
        return ret

    def getBestParameters(self):
        return self.__bestParameters

    def getBestResult(self):
        return self.__bestResult

    def getBestWorkerName(self):
        return self.__bestWorkerName

    def setBestResult(self, result, parameters, workerName):
        self.__bestResult = result
        self.__bestParameters = parameters
        self.__bestWorkerName = workerName


def _default_compare_func(x, y):
    return x.analyze_result.getSharpeRatio() > y.analyze_result.getSharpeRatio()


class Comparator(object):
    def __init__(self, compare_func=_default_compare_func):
        self._compare_func = compare_func

    def compare(self, x, y):
        return self._compare_func(x, y)

    def __call__(self, x, y):
        return self.compare(x, y)