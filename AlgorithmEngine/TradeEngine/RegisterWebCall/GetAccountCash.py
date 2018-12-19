def call():
    from TradeEngine.GlobleConf.AccountConf import AccountConf
    from Common.ExternalCommand import Handler

    def rt(tid):
        return AccountConf['account']

    Handler.subscribe('get_account_cash', rt)
