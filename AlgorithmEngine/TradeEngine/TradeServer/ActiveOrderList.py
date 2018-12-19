import threading


class ActiveOrderList(list):
    def __init__(self):
        super(ActiveOrderList, self).__init__()
        self.__lock = threading.Condition()

    def handler(self, func):
        self.__lock.acquire()
        try:
            rt = func(self)
        finally:
            self.__lock.release()
        return rt

    def __delitem__(self, key):
        self.__lock.acquire()
        try:
            super(ActiveOrderList, self).__delitem__(key)
        finally:
            self.__lock.release()

    def append(self, p_object):
        self.__lock.acquire()
        try:
            super(ActiveOrderList, self).append(p_object)
        finally:
            self.__lock.release()

    def remove(self, value):
        self.__lock.acquire()
        try:
            super(ActiveOrderList, self).remove(value)
        finally:
            self.__lock.release()
