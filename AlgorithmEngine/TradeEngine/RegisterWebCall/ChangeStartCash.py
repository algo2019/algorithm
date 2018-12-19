def call():
    from TradeEngine.GlobleConf import StrategyWidget
    from TradeEngine.MonitorClient import Monitor
    from TradeEngine.GlobleConf import StartConf
    from Common.ExternalCommand import Handler
    from Tables import StrategyTable

    st = StrategyTable.create()

    def rt(tid, strategy, add_num):
        if strategy not in st.get_strategy_of_sys(StartConf.PublishKey):
            Monitor.get_server_log('WebInsertOrderCmd').ERR(msg='unknown strategy %s' % strategy)
            return
        cash_added = float(add_num)
        Monitor.get_server_log('External_Web').INFO(strategy, 'Strategy:%s change start cash:%f' % (strategy, cash_added))
        StrategyWidget.get_account_mgr(strategy).update_start_cash(cash_added)

    Handler.subscribe('change_start_cash', rt)
