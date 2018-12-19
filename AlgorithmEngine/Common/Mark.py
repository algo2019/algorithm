
class Mark(object):
    def __init__(self):
        self.__mark_sign = 0

    def has_tag(self, mark):
        return self.__mark_sign | mark == self.__mark_sign

    def set_tag(self, mark):
        self.__mark_sign = self.__mark_sign | mark
