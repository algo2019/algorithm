from Common.Command import IntervalTradingDayCommand
from TradeEngine.GlobleConf import InfoUpdaterConf
from TradeEngine.GlobleConf import StartConf
from TradeEngine.GlobleConf import StrategyWidget
from TradeEngine.GlobleConf import Sys, SysWidget
from Common.Command import Command
from Common.RedisClient import getAutoRedisDict
import datetime

MAX_INTERESTS = 'MAX_INTERESTS_BY_DAY'
MAX_DRAW_DOWN = 'MAX_DRAW_DOWN_BY_DAY'


class RecordDrawDownByCloseCommand(Command):
    def __init__(self):
        super(RecordDrawDownByCloseCommand, self).__init__(name='UpdateMaxDrawDownByCloseCommand')
        self.__total_interests = 0
        self.__total_name = InfoUpdaterConf.total_account_name
        self.__dao = SysWidget.get_data_item_dao()

    def execute(self):
        self.__total_interests = 0
        for strategy in StrategyWidget.ACCOUNT:
            self.__update_for_one(strategy)
        self.__update_for_total()

    def __update_for_one(self, strategy):
        interests = StrategyWidget.get_account_mgr(strategy).interests
        self.__total_interests += interests
        self.__update_db(strategy, interests)

    def __update_db(self, strategy, interests):
        max_interests = self.__get_max(strategy, interests, MAX_INTERESTS)
        draw_down = max_interests - interests
        self.__dao.put(StartConf.PublishKey, strategy, 'MaxDrawDown', datetime.datetime.now(),
                       self.__get_max(strategy, draw_down, MAX_DRAW_DOWN))
        self.__dao.put(StartConf.PublishKey, strategy, 'MaxInterests', datetime.datetime.now(),
                       max_interests)
        self.__dao.put(StartConf.PublishKey, strategy, 'DrawDown', datetime.datetime.now(),
                       draw_down)

    @staticmethod
    def __get_max(strategy, value, redis_key):
        auto_dict = getAutoRedisDict(strategy, Sys.Sys)
        if value >= float(auto_dict[redis_key] or 0):
            auto_dict[redis_key] = value
            return value
        else:
            return float(auto_dict[redis_key])

    def __update_for_total(self):
        self.__update_db(self.__total_name, self.__total_interests)


def start_command():
    IntervalTradingDayCommand(InfoUpdaterConf.close_time, RecordDrawDownByCloseCommand())
