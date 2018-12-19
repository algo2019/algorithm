def call():
    from TradeEngine.GlobleConf import StartConf
    from TradeEngine.GlobleConf import ControllerV
    from TradeEngine.ctp_trade_engine import InsertArgs
    from TradeEngine.GlobleConf import SysWidget
    from Common.ExternalCommand import Handler
    from Tables import StrategyTable
    from TradeEngine.MonitorClient import Monitor
    st = StrategyTable.create()

    def insert_order(tid, name, type_str, offset, trade_side, instrument, volume, price):
        name, type_str, offset, trade_side, instrument = map(str, (name, type_str, offset, trade_side, instrument))
        if name not in st.get_strategy_of_sys(StartConf.PublishKey):
            Monitor.get_server_log('WebInsertOrderCmd').ERR(msg='unknown strategy %s' % name)
            return
        if price:
            price = float(price)

        if type_str == ControllerV.Position:
            is_local = False
        elif type_str == ControllerV.Shares:
            is_local = True
        else:
            raise Exception('is local ?')
        ia = InsertArgs(name, 'web', instrument, offset, trade_side, volume, price, 5, is_local=is_local)
        return SysWidget.get_trade_client().insert_order(ia)

    Handler.subscribe('web_insert_order', insert_order)
