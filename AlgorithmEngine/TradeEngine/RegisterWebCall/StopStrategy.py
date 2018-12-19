def call():
    from Common.ExternalCommand import Handler

    def rt(tid, strategy):
        from TradeEngine.StrategyControlCommand import StopCommand
        StopCommand(strategy).execute()

    Handler.subscribe('stop_strategy', rt)