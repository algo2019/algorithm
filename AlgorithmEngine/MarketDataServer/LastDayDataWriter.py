import cPickle as pickle
import datetime
import sys, os
import time
import json

sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..')))
from TradeEngine.OnBarDataStruct import OnBarData


class LastDayDataWriter(object):
    def __init__(self):
        import package_config
        from Common.RedisClient import RedisClient

        with open(package_config.config_file, 'r') as f:
            config = json.load(f)
        redis_host = config['redis_host']
        redis_port = config['redis_port']

        m_config = config['last_day_data_writer']
        redis_db = m_config['redis_db']

        self.db_key = m_config['db_key']
        self.tick_hkey = m_config['tick_hkey']
        self.day_hkey = m_config['day_hkey']

        self.__redis_reader = RedisClient(redis_host, redis_port, redis_db)

    def start(self):
        from MarketDataServer.MarketDataService import get_publish_name
        self.__redis_reader.subscribe(get_publish_name("00"), self.__process)
        while True:
            time.sleep(1)

    @staticmethod
    def get_dict_data(tick_data):
        return {item[0]: item[1] for item in (i.split('#') for i in tick_data['data'].split('|'))}

    def __process(self, tick_data):
        if tick_data['type'] != 'pmessage':
            return
        data = OnBarData(self.get_dict_data(tick_data))
        self.__write_to_redis(data)

    def __get_hkey(self, ins, is_tick=False):
        if is_tick:
            return "{}.{}".format(self.tick_hkey, ins)
        else:
            return "{}.{}".format(self.day_hkey, ins)

    def __write_to_redis(self, bar_data):
        write_msg = pickle.dumps((datetime.datetime.fromordinal(bar_data.DateTime.date().toordinal()), bar_data.DayOpen, bar_data.DayHigh, bar_data.DayLow,
                                  bar_data.DayClose, bar_data.DayVolume))
        self.__redis_reader.hset(self.db_key, self.__get_hkey(bar_data.InstrumentID, False), write_msg)
        self.__redis_reader.hset(self.db_key, self.__get_hkey(bar_data.InstrumentID, True), pickle.dumps(bar_data))


if __name__ == '__main__':
    LastDayDataWriter().start()