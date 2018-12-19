# -*- coding: utf-8 -*-
"""
syswidget.py
"""


class SysWidget(object):
    """
    SysWidget
    """
    LOCAL_REMOTE_REF_MAPPER = None
    REDIS_READER = None
    TICK_DATA = None
    ACTIVE_ORDER_LIST = None
    TRADE_CLIENT = None
    ADJUST_OPERATOR = None
    REMOTE_STRATEGY_CALLER = None
    REMOTE_STRATEGY_CONTROLLER = None
    MONITOR_SERVER = None
    MONITOR_CLIENT = None
    ON_RTN_EVENT_DIVER = None
    INFO_UPDATER = None
    WEB_DATA = None
    ERR_MSG_SENDER = None
    THREAD_ENGINE = None
    LOG_ENGINE = None
    MAIN_ENGINE = None
    LOGERS = {}
    TRADE_LOG_DAO = None
    DATA_ITEM_DAO = None
    REMOTE_SERVICE = None
    JSON_CONFIG = None
    SERVICE_LOGGER = {}

    @classmethod
    def get_main_engine(cls):
        if cls.MAIN_ENGINE is None:
            from Common.AtTimeObjectEngine import ThreadEngine
            cls.MAIN_ENGINE = ThreadEngine('Main')
            cls.MAIN_ENGINE.start()
        return cls.MAIN_ENGINE

    @classmethod
    def get_external_engine(cls):
        if cls.THREAD_ENGINE is None:
            from Common.AtTimeObjectEngine import ThreadEngine
            cls.THREAD_ENGINE = ThreadEngine('External')
            cls.THREAD_ENGINE.start()
        return cls.THREAD_ENGINE

    @classmethod
    def get_log_engine(cls):
        if cls.LOG_ENGINE is None:
            from Common.AtTimeObjectEngine import ThreadEngine
            cls.LOG_ENGINE = ThreadEngine('Log')
            cls.LOG_ENGINE.start()
        return cls.LOG_ENGINE

    @classmethod
    def get_info_updater(cls):
        if cls.INFO_UPDATER is None:
            from TradeEngine.TradeServer.InfoUpdater import InfoUpdater
            cls.INFO_UPDATER = InfoUpdater()
        return cls.INFO_UPDATER

    @classmethod
    def get_on_rtn_event_diver(cls):
        if cls.ON_RTN_EVENT_DIVER is None:
            from TradeEngine.TradeServer.OnRtnEventDiver import OnRtnEventDiver
            cls.ON_RTN_EVENT_DIVER = OnRtnEventDiver()
        return cls.ON_RTN_EVENT_DIVER

    @classmethod
    def get_remote_strategy_controller(cls):
        if cls.REMOTE_STRATEGY_CONTROLLER is None:
            from TradeEngine.TradeServer.RemoteControl import RemoteStrategyController
            cls.REMOTE_STRATEGY_CONTROLLER = RemoteStrategyController()
        return cls.REMOTE_STRATEGY_CONTROLLER

    @classmethod
    def get_monitor_client(cls, strategy_name=None):
        if cls.MONITOR_CLIENT is None:
            if strategy_name is None:
                raise Exception('MonitorClient not init')
            from TradeEngine.MonitorClient.Monitor import Monitor
            cls.MONITOR_CLIENT = Monitor.create(strategy_name)
        return cls.MONITOR_CLIENT

    @classmethod
    def get_remote_strategy_caller(cls, strategy_name=None):
        if cls.REMOTE_STRATEGY_CALLER is None:
            if strategy_name is None:
                raise Exception('RemoteSrategyCaller not init')
            from TradeEngine.TradeClient.RemoteStrategyCaller import RemoteStrategyCaller
            from TradeEngine.GlobleConf import StartConf
            cls.REMOTE_STRATEGY_CALLER = RemoteStrategyCaller(strategy_name, StartConf.RemoteServiceHost,
                                                              StartConf.RemoteServicePort)
        return cls.REMOTE_STRATEGY_CALLER

    @classmethod
    def get_active_order_list(cls):
        if cls.ACTIVE_ORDER_LIST is None:
            from TradeEngine.TradeServer.ActiveOrderList import ActiveOrderList
            cls.ACTIVE_ORDER_LIST = ActiveOrderList()
        return cls.ACTIVE_ORDER_LIST

    @classmethod
    def get_adjust_operator(cls):
        if cls.ADJUST_OPERATOR is None:
            from TradeEngine.TradeServer.AdjustOperator import AdjustOperator
            cls.ADJUST_OPERATOR = AdjustOperator()
        return cls.ADJUST_OPERATOR

    @classmethod
    def get_tick_data(cls):
        if cls.TICK_DATA is None:
            from TradeEngine.TradeServer.TickData import TickData
            cls.TICK_DATA = TickData()
        return cls.TICK_DATA

    @classmethod
    def get_redis_reader(cls, redis_host=None, redis_port=6379, db=0):
        if redis_host is not None:
            from Common.RedisClient import RedisClient
            if cls.REDIS_READER is None:
                cls.REDIS_READER = RedisClient(redis_host, redis_port, db)
        elif cls.REDIS_READER is None:
            from Common.RedisClient import RedisClient
            from TradeEngine.GlobleConf import StartConf
            cls.REDIS_READER = RedisClient(StartConf.RedisHost, StartConf.RedisPort, StartConf.RedisDB)
        return cls.REDIS_READER

    @classmethod
    def get_monitor_server(cls):
        if cls.MONITOR_SERVER is None:
            from TradeEngine.MonitorService import MonitorService
            cls.MONITOR_SERVER = MonitorService()
        return cls.MONITOR_SERVER

    @classmethod
    def get_trade_client(cls):
        if cls.TRADE_CLIENT is None:
            from TradeEngine.ctp_trade_engine import CTPTradeEngine, CTPTradeEngineConfig
            from TradeEngine.GlobleConf import StartConf
            CTPTradeEngineConfig.set(StartConf.CTPTradeHost, StartConf.BrokerId, StartConf.UserId, StartConf.Password,
                                     StartConf.PublishKey, StartConf.RedisHost, StartConf.RedisPort)
            cls.TRADE_CLIENT = CTPTradeEngine()
        return cls.TRADE_CLIENT

    @classmethod
    def get_local_remote_ref_mapper(cls):
        if cls.LOCAL_REMOTE_REF_MAPPER is None:
            from TradeEngine.TradeServer import LocalRemoteRefMap
            cls.LOCAL_REMOTE_REF_MAPPER = LocalRemoteRefMap.LocalRemoteRefMap()
        return cls.LOCAL_REMOTE_REF_MAPPER

    @classmethod
    def get_logger(cls, source, name=None):
        key = '{}.{}'.format(source, name)
        if cls.LOGERS.get(key) is None:
            from mlogging import MyLogger
            cls.LOGERS[key] = MyLogger(source, name)
        return cls.LOGERS[key]

    @classmethod
    def get_service_logger(cls, source, log_name='logger'):
        key = '{}.{}'.format(source, log_name)
        if cls.SERVICE_LOGGER.get(key) is None:
            from mlogging import MyServerLogger
            cls.SERVICE_LOGGER[key] = MyServerLogger(source, log_name)
        return cls.SERVICE_LOGGER[key]

    @classmethod
    def get_trade_log_dao(cls):
        if cls.TRADE_LOG_DAO is None:
            from Common.Dao import TradeRecordDao
            cls.TRADE_LOG_DAO = TradeRecordDao()
        return cls.TRADE_LOG_DAO

    @classmethod
    def get_data_item_dao(cls):
        if cls.DATA_ITEM_DAO is None:
            from Common.Dao import DataItemDao
            cls.DATA_ITEM_DAO = DataItemDao()
        return cls.DATA_ITEM_DAO

    @classmethod
    def get_remote_service(cls):
        if cls.REMOTE_SERVICE is None:
            from TradeEngine.TradeServer.RemoteService import RemoteService
            from TradeEngine.GlobleConf import StartConf
            cls.REMOTE_SERVICE = RemoteService(StartConf.RemoteServicePort, StartConf.RemoteServiceHost)
        return cls.REMOTE_SERVICE

    @classmethod
    def get_json_config(cls):
        if cls.JSON_CONFIG is None:
            try:
                import package_config, json
                with open(package_config.config_file) as f:
                    cls.JSON_CONFIG = json.load(f)
            except Exception as e:
                cls.get_logger('json_config').INFO("Con't load config:{}".format(str(e)))
        return cls.JSON_CONFIG
