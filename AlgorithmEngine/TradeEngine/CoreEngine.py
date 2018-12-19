# encoding: utf-8
"""
CoreEngine.py
    load strategy and config
    入口参数：publish_key, strategy, unique_str
"""
import sys
import os
import time


def get_core_engine(*args, **kwargs):
    """
    :param args: 
    :param kwargs: 
    :return: class of CoreEngine
    """
    import importlib
    from TradeEngine.GlobleConf import SysWidget, StartConf

    class Config(object):
        """
        策略配置对象
        """

        def __init__(self, configs, key):
            self.__name = key
            self.__param = configs[key]['param']
            self.__instrument_and_periods = configs[key]['instruments']
            self.__instruments = list({iap[0] for iap in self.__instrument_and_periods})

        @property
        def name(self):
            """
            :return: 策略名称 
            """
            return self.__name

        @property
        def param(self):
            """
            :return: 策略参数 
            """
            return self.__param

        @property
        def instruments(self):
            """
            :return: 订阅合约
            """
            return self.__instruments

        @property
        def instruments_and_period(self):
            """
            :return: 订阅合约及其周期 
            """
            return self.__instrument_and_periods

    class CoreEngineConf(object):
        """
        策略启动配置对象
        """

        def __init__(self, conf):
            self.__redis_host = StartConf.RedisHost
            self.__redis_port = StartConf.RedisPort
            self.__strategy_name = conf['StrategyName']
            self.__strategy_file_name = conf.get('StrategyFile', '').split('.')[0]
            self.__configs = []
            self.__parse_configs(conf['configs'])

        def __parse_configs(self, configs):
            for key in configs:
                self.configs.append(Config(configs, key))

        @property
        def strategy_file_name(self):
            """
            :return: 策略程序文件名称 
            """
            return self.__strategy_file_name

        @property
        def configs(self):
            """
            :return: 策略配置对象 
            """
            return self.__configs

        @property
        def redis_host(self):
            """
            :return:  
            """
            return self.__redis_host

        @property
        def redis_port(self):
            """
            :return: 
            """
            return self.__redis_port

        @property
        def strategy_name(self):
            """
            :return: 
            """
            return self.__strategy_name

    class CoreEngine(object):
        """
        策略启动器
        """

        def __init__(self, conf):
            # type: (dict) -> None
            self.conf = CoreEngineConf(conf)
            from TradeEngine.GlobleConf import SysWidget
            self.__logger = SysWidget.get_logger('CoreEngine')
            self.init_strategy()
            self.init_redis_and_monitor()
            self.__logger.INFO('CoreEngine instance init ok')

        @classmethod
        def load_sys_conf(cls, strategy_name, strategy_path):
            # type: (str, str) -> dict
            """
            :param strategy_name: 
            :param strategy_path: 
            :return: core_engine config dict
            """
            context_path, strategy_file = os.path.split(strategy_path)
            configs = cls.load_configs(context_path)
            conf = {'StrategyFile': strategy_file,
                    'StrategyName': strategy_name,
                    'configs': configs}
            return conf

        def init_redis_and_monitor(self):
            """
            初始化系统组件
            :return:
            """
            if SysWidget.REDIS_READER is None:
                SysWidget.get_redis_reader(self.conf.redis_host, self.conf.redis_port, StartConf.RedisDB)
            if SysWidget.MONITOR_CLIENT is None:
                SysWidget.get_monitor_client(self.conf.strategy_name).startHeartBeat()
            if SysWidget.REMOTE_STRATEGY_CALLER is None:
                SysWidget.get_remote_strategy_caller(self.conf.strategy_name).start()
            self.__logger.INFO('init_redis_and_monitor ready')

        def init_strategy(self):
            # type: () -> None
            """
            策略初始化
            :return:
            """
            from TradeEngine.GlobleConf import StrategyWidget
            StrategyWidget.register_strategy([self.conf.strategy_name])
            self.__logger.INFO('init_strategy ready')

        @classmethod
        def load_configs(cls, context_path):
            # type: (str) -> dict
            """
            加载策略配置
            :param context_path: 
            :return: strategy configs
            """
            sys.path.insert(0, context_path)
            import context
            return context.configs

        def get_strategy(self):
            # type: () -> callable
            """
            加载策略类
            :return: 
            """
            self.__logger.INFO('loading module: {}'.format(self.conf.strategy_file_name))
            module = importlib.import_module(self.conf.strategy_file_name)
            return getattr(module, self.conf.strategy_name)

        def start_engine(self, strategy_class=None):
            # type: (callable) -> dict
            """
            :param strategy_class: 
            :return: 
            """
            conf = self.conf
            strategies = {}
            SysWidget.get_redis_reader().clearStates(self.conf.strategy_name)
            if strategy_class is None:
                self.__logger.INFO('loadStrategy')
                strategy_class = self.get_strategy()
            if strategy_class is None:
                self.__logger.ERR('strategy_class is None')
                return strategies
            self.__logger.INFO('strategy starting')
            # 根据配置实例化策略
            for config in conf.configs:
                self.__logger.INFO('%s.%s %s starting', conf.strategy_name, config.name,
                                   str(config.instruments_and_period))
                key = '%s.%s' % (conf.strategy_name, config.name)
                if strategies.get(key) is not None:
                    raise Exception('start engine key is exists yet:{}'.format(key))

                strategies[key] = strategy_class(conf.strategy_name, config)
            # 启动所有策略实例
            map(lambda x: x.start(), strategies.values())
            self.__logger.INFO('strategy started')
            return strategies

    return CoreEngine


# noinspection PyUnresolvedReferences
def external_import():
    # type: () -> None
    """
    import the package of strategies needed
    """
    from TradeEngine.TradeClient.BaseStrategy import BaseStrategy
    import dataServer
    from dataServer import dataServer, d
    import tradeutil


def send_heartbeat_wait(strategy_name):
    # type: () -> None
    # 心跳 key
    """
    发送心跳并等待结束命令
    """
    from TradeEngine.GlobleConf.RedisKey import Publish
    from TradeEngine.GlobleConf import Sys, SysWidget
    heart_beat_key = Publish.HeartBeat(strategy_name)
    r = SysWidget.get_redis_reader()
    # 停止标识用于外部停止命令
    while not Sys.Stoped:
        # 发送进程心跳
        r.publish(heart_beat_key, str(time.time()))
        time.sleep(1)


def run(publish_key, strategy_name):
    from TradeEngine import GlobleConf

    # 根据配置数据库初始化当前系统参数
    GlobleConf.init_conf(publish_key)
    from TradeEngine.GlobleConf import SysWidget

    logger = SysWidget.get_logger('CoreEngine', strategy_name)
    # 引用策略中需要的额外包，用于打包
    external_import()
    try:
        logger.INFO('CoreEngine: start')
        from Tables import StrategyTable

        strategy_path = StrategyTable.create().get_start_conf(publish_key, strategy_name)[0]
        # 策略路径为空则退出
        if not strategy_path or strategy_path == 'None':
            logger.WARN("{}'s strategy_path is None")
        else:
            CoreEngine = get_core_engine()
            logger.INFO('load_sys_conf running')
            # 获取策略配置信息
            conf = CoreEngine.load_sys_conf(strategy_name, strategy_path)
            logger.INFO('CoreEngine instance running')
            ce = CoreEngine(conf)
            logger.INFO('start_engine running')
            # 启动策略
            strategies = ce.start_engine()
            map(logger.INFO, GlobleConf.show_msg().split('\n'))
            logger.INFO('start_engine over')

            if len(strategies) > 0:
                send_heartbeat_wait(strategy_name)
            else:
                logger.WARN('length of strategy is 0')
    except:
        import traceback

        print traceback.format_exc()
        logger.ERR(traceback.format_exc())


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "参数错误！"
        sys.exit(0)
    publish_key = sys.argv[1]
    strategy_name = sys.argv[2]
    run(publish_key, strategy_name)
