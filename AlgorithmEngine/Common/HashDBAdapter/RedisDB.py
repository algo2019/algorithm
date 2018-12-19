from HashDBAdapter import HashDBAdapter
import redis


class RedisDB(HashDBAdapter):

    def __init__(self, host, port, db):
        self.__redis = redis.StrictRedis(host, port, db)

    def hgetall(self, key):
        return self.__redis.hgetall(key)

    def values(self, key_list):
        context = {}
        for key in key_list:
            type = self.__redis.type(key)
            if type == "hash":
                context[key] = self.__redis.hgetall(key)
            elif type == "string":
                context[key] = self.__redis.get(key)
            elif type == "set":
                context[key] = self.__redis.smembers(key)
            else:
                continue
        return context

    def hget(self, key, field):
        return self.__redis.hget(key, field)

    def delete(self, key):
        for key_ in self.keys(key):
            self.__redis.delete(key_)

    def hmset(self, key, mapping):
        self.__redis.hmset(key, mapping)

    def keys(self, key=None):
        if key is None:
            key = '*'
        return self.__redis.keys(key)

    def hset(self, key, field, value):
        self.__redis.hset(key, field, value)

    def hdel(self, key, field):
        self.__redis.hdel(key, field)

    def type(self, name):
        return self.__redis.type(name)

    def rename(self, src, dst):
        return self.__redis.rename(src, dst)
