# coding=utf-8
import redis
import cPickle as pickle
from TradeEngine.OnBarDataStruct import OnBarData


class _TickDataDao(object):
    def __init__(self, sub_key, redis_conf, db_key):
        self.__key = db_key
        self.__sub_key = sub_key
        self.__redis_save = redis.StrictRedis(*redis_conf)

    def start_update_redis_wait(self):
        ps = self.__redis_save.pubsub()
        ps.psubscribe(self.__sub_key)
        for msg in ps.listen():
            if msg['type'] != 'pmessage':
                continue
            self.__process(msg)

    @staticmethod
    def get_dict_data(tick_data):
        return {item[0]: item[1] for item in (i.split('#') for i in tick_data['data'].split('|'))}

    def __process(self, tick_data):
        data = OnBarData(self.get_dict_data(tick_data))
        self.__write_to_redis(data)

    def __write_to_redis(self, bar_data):
        self.__redis_save.hset(self.__key, bar_data.InstrumentID.upper(), pickle.dumps(bar_data))

    def get(self, instrument):
        if instrument == '*':
            all_ins = self.__redis_save.hgetall(self.__key)
            for key in all_ins:
                all_ins[key] = pickle.loads(all_ins[key])
            return all_ins

        data = self.__redis_save.hget(self.__key, instrument.upper())
        if data is None:
            data = self.__redis_save.hget(self.__key, instrument)
            if data is None:
                return None
        return pickle.loads(data)


def TickDataDao():
    """
    尝试在配置文件中获取配置，否则使用默认配置创建TickDataDao实例
    :return: _TickDataDao 实例 
    """
    try:
        import package_config
        import os
        config_file = package_config.config_file
        if os.path.exists(config_file):
            import json
            with open(config_file) as f:
                config = json.load(f)
            pub_key = "{}.*".format(config['market_data']['publish_key'])
            redis_db = config['tick_dao']['redis_db']
            redis_host = config['redis_host']
            redis_port = config['redis_port']
            db_key = config['tick_dao']['db_key']
            print 'TickDataDao load config file:', config_file
            return _TickDataDao(pub_key, (redis_host, redis_port, redis_db), db_key)
        else:
            raise Exception('config file is not exists: {}'.format(package_config.config_file))
    except Exception as e:
        raise Exception('TickDataDao load config file err: {}'.format(str(e)))


if __name__ == '__main__':
    TickDataDao().start_update_redis_wait()
