def start():
    from TradeEngine import GlobleConf
    from TradeEngine.GlobleConf import SysWidget
    from TradeEngine.MonitorClient import Monitor
    from TradeEngine.GlobleConf import StartConf, Sys
    from Common import ExternalCommand

    class ServerApp(object):
        def __init__(self):
            self.redis_host = StartConf.RedisHost
            self.redis_port = StartConf.RedisPort
            self.db_num = StartConf.RedisDB
            self.__name = Sys.ServerApp
            self.__started = False
            self.__logger = None
            self.init_sys_widget()
            self.init_strategies()
            print StartConf.TradeHost, StartConf.TradePort, StartConf.PublishKey

        def init_sys_widget(self):
            if SysWidget.REDIS_READER is None:
                SysWidget.get_redis_reader(self.redis_host, self.redis_port, self.db_num)
                SysWidget.get_monitor_client(self.__name)
            self.__logger = Monitor.get_logger(self.__name)

        @staticmethod
        def init_strategies():
            from Tables import StrategyTable
            from TradeEngine.GlobleConf import StrategyWidget
            StrategyWidget.register_strategy(StrategyTable.create().get_strategy_of_sys(StartConf.PublishKey))

        def start(self):
            if not self.__started:
                self.__started = True
                SysWidget.get_monitor_server().start()
                map(self.__logger.INFO, GlobleConf.show_msg().split('\n'))
                SysWidget.get_on_rtn_event_diver().start()
                SysWidget.get_remote_strategy_controller().start()
                SysWidget.get_remote_service().start()
                SysWidget.get_trade_client().start()
                SysWidget.get_info_updater().start()
                SysWidget.get_adjust_operator().start()
                ExternalCommand.get_executor(SysWidget.get_redis_reader(), StartConf.PublishKey, SysWidget.get_external_engine()).start()
                self.__logger.INFO('started')
            else:
                self.__logger.WARN('start:can start again!')
            self.__logger.INFO('publish_key:%s redis:%s %d %d trade:%s %d', StartConf.PublishKey, StartConf.RedisHost,
                               StartConf.RedisPort, StartConf.RedisDB, StartConf.TradeHost, StartConf.TradePort)
            return self
    ServerApp().start()


def register_web_action():
    from TradeEngine.MonitorClient import Monitor
    logger = Monitor.get_server_log('register_web_action')
    try:
        from TradeEngine import RegisterWebCall
        RegisterWebCall.register()
        logger.INFO(msg='register ok')
    except:
        import traceback
        logger.ERR(msg=traceback.format_exc())


def main(pk):
    import sys, time, os
    sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..')))

    from TradeEngine import GlobleConf

    GlobleConf.init_conf(pk)
    start()
    register_web_action()
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        raise Exception('need publish_key as argv')
    main(sys.argv[1])