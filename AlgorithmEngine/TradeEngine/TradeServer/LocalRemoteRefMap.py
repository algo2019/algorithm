class LocalRemoteRefMap(object):
    def __init__(self):
        self.__local_ref_to_strategy_name = {}
        self.__local_to_instrument = {}
        self.__local_to_name = {}

    def set(self, local, strategy_name=None, strategy_object_name=None, instrument=None):
        if strategy_name is not None:
            self.__local_ref_to_strategy_name[local] = strategy_name
        if instrument:
            self.__local_to_instrument[local] = instrument
        if strategy_object_name:
            self.__local_to_name[local] = strategy_object_name

    def get_instrument(self, local):
        return self.__local_to_instrument[local]

    def get_strategy_object_name(self, local):
        return self.__local_to_name[local]

    def get_strategy_name(self, local):
        return self.__local_ref_to_strategy_name[local]