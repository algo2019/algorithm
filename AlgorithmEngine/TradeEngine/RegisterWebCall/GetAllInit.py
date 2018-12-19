def get_conf():
    return {
        'DB_KEY': 'MONITOR.ACCOUNT',
        'INTERVAL': 1
    }


def call():
    import json
    from TradeEngine.GlobleConf import SysWidget, StrategyWidget, RedisKey, InfoUpdaterConf
    from Common.Command import Command, IntervalCommand
    from TradeEngine.GlobleConf import Sys
    from TradeEngine.MonitorClient import Monitor
    from TradeEngine.GlobleConf import StartConf
    from TradeEngine.GlobleConf.AccountConf import BackTestDrawDown
    import traceback
    import datetime
    global get_conf

    CONF = get_conf()

    class UpdateAccountCommand(Command):
        def __init__(self):
            super(UpdateAccountCommand, self).__init__(name='UpdateAllInitCommand')
            self.total_name = InfoUpdaterConf.total_account_name
            self.__total_nums = None
            self.__redis = SysWidget.get_redis_reader()
            self.__max_draw_down_by_day = '-1'
            self.__cur_date = None
            self.__rf = False

        @staticmethod
        def __is_next_day():
            close = datetime.time(15, 1, 0)
            if hasattr(Sys, 'today'):
                r_ = getattr(Sys, 'today')
                r_d, r_t = r_.date(), r_.time()
                now = datetime.datetime.now()
                d, t = now.date(), now.time()
                if r_d == d:
                    if r_t > close and t > close:
                        return False
                    elif r_t <= close and t <= close:
                        return False
                elif r_d < d and r_t > close > t:
                    return False
            setattr(Sys, 'max_draw_down_by_day', {})
            setattr(Sys, 'today', datetime.datetime.now())
            return True

        def execute(self):
            self.__total_nums = None
            self.__rf = False
            try:
                if self.__is_next_day():
                    self.__rf = True
                self.__total_nums = None
                self._update_each_strategy()
                self._update_total()
                self.__rf = False
            except RuntimeError, e:
                if str(e) != 'dictionary changed size during iteration':
                    raise

        def __get_max_draw_by_day(self, strategy):
            try:
                if self.__rf:
                    Sys.max_draw_down_by_day[strategy] = \
                        SysWidget.get_data_item_dao().get_last(StartConf.PublishKey, strategy, 'MaxDrawDown')[1]
            except:
                Sys.max_draw_down_by_day[strategy] = '-1'
            return Sys.max_draw_down_by_day[strategy]

        def _update_each_strategy(self):
            for strategy in StrategyWidget.ACCOUNT:
                try:
                    nums = self._get_strategy_nums(strategy)
                    account = [strategy] + map(lambda x: '%2.2f' % x, nums) + [self.__get_max_draw_by_day(strategy),
                         BackTestDrawDown.get(strategy, -1)] + self._get_strategy_state(strategy)
                    self._update_total_num(nums)
                    self.__redis.hset(CONF['DB_KEY'], strategy, json.dumps(account))
                except:
                    Monitor.get_server_log(self.name).ERR(strategy, traceback.format_exc())

        def _update_total_num(self, nums):
            if self.__total_nums is None:
                self.__total_nums = [0 for i in xrange(len(nums))]
            for i in xrange(len(nums)):
                self.__total_nums[i] += nums[i]

        def _update_total(self):
            if self.__total_nums is None:
                return
            max_interests = self._update_total_max_interests()
            self._update_draw_downs(max_interests)
            total_account = [self.total_name] + map(lambda x: '%2.2f' % x, self.__total_nums) + [
                self.__get_max_draw_by_day(self.total_name), BackTestDrawDown.get(self.total_name, -1), '-', '-']
            self.__redis.hset(CONF['DB_KEY'], self.total_name, json.dumps(total_account))

        @staticmethod
        def _get_strategy_nums(strategy):
            account_mgr = StrategyWidget.get_account_mgr(strategy)
            return [
                account_mgr.start_cash,
                account_mgr.interests,
                account_mgr.cash,
                account_mgr.curr_margin,
                account_mgr.commission,
                account_mgr.position_profit,
                account_mgr.close_profit,
                account_mgr.draw_down_cash,
                account_mgr.max_draw_down_cash
            ]

        @staticmethod
        def _get_strategy_state(strategy):
            monitor_server = SysWidget.get_monitor_server()
            return [monitor_server.get_state(strategy),
                    str(monitor_server.get_heart_beat(strategy))[:19]]

        def _get_total_max_draw_down_in_redis(self):
            return self._init_redis_num(SysWidget.get_redis_reader().hget(
                RedisKey.DB.Strategy.AutoSaveDictOfStrategy(self.total_name, self.total_name),
                RedisKey.DB.Strategy.Account()))

        @staticmethod
        def _init_redis_num(str_num, default=0):
            if str_num is None:
                return default
            return float(str_num)

        def _get_total_max_interests_in_redis(self):
            return self._init_redis_num(SysWidget.get_redis_reader().hget(
                RedisKey.DB.Strategy.AutoSaveDictOfStrategy(self.total_name, self.total_name),
                RedisKey.DB.Strategy.Interests()))

        def _update_total_max_interests(self):
            max_interests = self._get_total_max_interests_in_redis()
            if self.__total_nums[1] > max_interests:
                max_interests = self.__total_nums[1]
                SysWidget.get_redis_reader().hset(
                    RedisKey.DB.Strategy.AutoSaveDictOfStrategy(self.total_name, self.total_name),
                    RedisKey.DB.Strategy.Interests(), max_interests)
            return max_interests

        def _update_draw_downs(self, max_interests):
            max_draw_down_cash = self._get_total_max_draw_down_in_redis()
            self.__total_nums[-2] = max_interests - self.__total_nums[1]
            if self.__total_nums[-2] > max_draw_down_cash:
                max_draw_down_cash = self.__total_nums[-2]
                SysWidget.get_redis_reader().hset(
                    RedisKey.DB.Strategy.AutoSaveDictOfStrategy(self.total_name, self.total_name),
                    RedisKey.DB.Strategy.Account(), max_draw_down_cash)
            self.__total_nums[-1] = max_draw_down_cash
            return max_draw_down_cash

    IntervalCommand(CONF['INTERVAL'], UpdateAccountCommand(), SysWidget.get_external_engine())
