import threading
import cPickle as pick
from TradeEngine.GlobleConf import RedisKey
from TradeEngine.GlobleConf import SysEvents, SysWidget
from HashDBAdapter.RedisDB import RedisDB
from PubSubAdapter.RedisPubSub import RedisPubSub


class RedisClient(RedisDB, RedisPubSub):
    def __init__(self, host, port=6379, db=0):
        RedisDB.__init__(self, host, port, db)
        RedisPubSub.__init__(self, host, port)
        SysEvents.Publish.subscribe(self.publish)

    def setState(self, strategy_name, obj_name, key, value):
        self.hset(RedisKey.DB.Web.States(strategy_name, obj_name), key, str(value))

    def setStates(self, strategy_name, obj_name, state_dict):
        self.hmset(RedisKey.DB.Web.States(strategy_name, obj_name), state_dict)

    def clearStates(self, strategy_name):
        self.delete(RedisKey.DB.Web.States(strategy_name))


class AutoRedisDict(dict):
    def __init__(self, key, **kwargs):
        super(AutoRedisDict, self).__init__(**kwargs)
        self.__lock = threading.Lock()
        self.__key = key
        self.__client = SysWidget.get_redis_reader()

    def __getitem__(self, item):
        self.__lock.acquire()
        if item not in self:
            rs = self.__client.hget(self.__key, item)
            if rs:
                super(AutoRedisDict, self).__setitem__(item, pick.loads(rs))
        self.__lock.release()
        return self.get(item)

    def __setitem__(self, key, value):
        self.__lock.acquire()
        self.__client.hset(self.__key, key, pick.dumps(value))
        super(AutoRedisDict, self).__setitem__(key, value)
        self.__lock.release()

    def get_with_update(self, item):
        self.__lock.acquire()
        rs = self.__client.hget(self.__key, item)
        if rs:
            super(AutoRedisDict, self).__setitem__(item, pick.loads(rs))
        self.__lock.release()
        return self.get(item)

    __DICTS = {}

    @classmethod
    def create(cls, strategyName, key):
        fullKey = RedisKey.DB.Strategy.AutoSaveDictOfStrategy(strategyName, key)
        if not cls.__DICTS.get(fullKey):
            cls.__DICTS[fullKey] = cls(fullKey)
        return cls.__DICTS[fullKey]


def getAutoRedisDict(strategyName, key):
    return AutoRedisDict.create(strategyName, key)


def getRedisReader(host=None, port=6379, db=0):
    return RedisClient(host, port, db)
