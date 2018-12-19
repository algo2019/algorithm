from TradeEngine.GlobleConf.RedisKey import DB
from RemoteAccountWriter import RemoteAccountWriter


class RedisWriter(RemoteAccountWriter):

    def __init__(self, redis=None):
        if redis is None:
            from TradeEngine.GlobleConf import SysWidget
            self.__redis = SysWidget.get_redis_reader()
        else:
            self.__redis = redis

    def write(self, cache_dice):
        self.__redis.hmset(DB.Remote.Account(), cache_dice)

    def read(self):
        return self.__redis.values([DB.Remote.Account()])[DB.Remote.Account()]
