import cPickle
import redis

pk_db = {}
pk_hp = {}


def get_db(publish_key):
    if pk_db.get(publish_key) is None:
        from Tables import ConfTable
        pk_db[publish_key] = int(ConfTable.create().select_conf(publish_key, 'REDIS_DB'))
    return pk_db[publish_key]


def get_host_port(publish_key):
    if pk_hp.get(publish_key) is None:
        from Tables import ConfTable
        ct = ConfTable.create()
        pk_hp[publish_key] = (ct.select_conf(publish_key, 'REDIS_HOST'), int(ct.select_conf(publish_key, 'REDIS_PORT')))
    return pk_hp[publish_key]


class State(object):
    def __init__(self, publish_key, strategy_name, instance_name):
        self.redis_client = redis.StrictRedis(*get_host_port(publish_key), db=get_db(publish_key))
        self.db_key = self.get_key(strategy_name, instance_name)

    def set_state_map(self, mapping):
        self.redis_client.hmset(self.db_key, mapping)

    def set_state(self, key, value):
        self.redis_client.hset(self.db_key, key, str(value))

    def get_all_state(self):
        return self.redis_client.hgetall(self.db_key)

    @classmethod
    def get_key(cls, strategy_name, instance_name):
        return 'WEB.STATES.%s.%s' % (strategy_name, instance_name)


class AutoSave(object):
    def __init__(self, publish_key, strategy_name, instance_name):
        self.redis_client = redis.StrictRedis(*get_host_port(publish_key), db=get_db(publish_key))
        self.db_key = 'AUTO_SAVE.%s.%s' % (strategy_name, instance_name)

    def get_key(self, key):
        return cPickle.loads(self.redis_client.hget(self.db_key, key))

    def set_key(self, key, value):
        self.redis_client.hset(self.db_key, key, cPickle.dumps(value))

    def get_all(self):
        rt = self.redis_client.hgetall(self.db_key)
        for key in rt:
            rt[key] = cPickle.loads(rt[key])
        return rt
