import abc


class BaseRole(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.__or_role = []
        self.__and_role = []

    @abc.abstractmethod
    def _self_check(self, h, m, s):
        raise NotImplementedError

    def check(self, h, m, s):
        for role in self.__and_role:
            if not role.check(h, m, s):
                return False

        for role in self.__or_role:
            if role.check(h, m, s):
                return True

        return self._self_check(h, m, s)

    def add_or_role(self, role):
        self.__or_role.append(role)

    def add_and_role(self, role):
        self.__and_role.append(role)
