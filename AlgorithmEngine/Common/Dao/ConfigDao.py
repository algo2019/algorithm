from Common.HashDBAdapter.RedisDB import RedisDB


class Config(object):
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 15

try:
    import package_config
    import os
    config_file = package_config.config_file
    if os.path.exists(config_file):
        import json
        with open(config_file) as f:
            config = json.loads(f.read())
        Config.REDIS_HOST = config['redis_host']
        Config.REDIS_PORT = config['redis_port']
        Config.REDIS_DB = config['config_dao']['redis_db']
        print 'ConfigDao load config file:', config_file
    else:
        raise Exception('config file not found')
except Exception as e:
    print 'ConfigDao load from config file err:', package_config.config_file, str(e)


class ConfigDao(object):
    DEFAULT = 'DEFAULT'

    def __init__(self, prefix=''):
        self.__redis_host = Config.REDIS_HOST
        self.__redis_port = Config.REDIS_PORT
        self.__redis_db = Config.REDIS_DB
        self.__redis = RedisDB(self.__redis_host, self.__redis_port, self.__redis_db)
        self.__prefix = prefix

    def key(self, system):
        return '{}{}'.format(self.__prefix, system)

    def set(self, system, key, value):
        self.__redis.hset(self.key(system), key, value)

    def set_map(self, system, mapping):
        self.__redis.hmset(self.key(system), mapping)

    def get(self, system, key):
        return self.__redis.hget(self.key(system), key)

    def get_all(self, system=None):
        if system is None or '*' in system:
            return self.__redis.values(self.__redis.keys(self.key(system or '*')))
        return self.__redis.hgetall(self.key(system))

    def delete(self, system, key=None):
        if key is None:
            self.__redis.delete(self.key(system))
        else:
            self.__redis.hdel(self.key(system), key)

    def select_all(self):
        return self.get_all()

    def select_sys(self, system):
        return self.get_all(system)

    def select_conf(self, system, key):
        return self.get(system, key)

    def get_conf(self, system):
        res = self.__redis.hgetall(self.key(self.DEFAULT))
        res.update(self.__redis.hgetall(self.key(system)))
        return res
