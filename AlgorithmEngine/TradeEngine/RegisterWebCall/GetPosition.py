def call():
    from Common.Command import IntervalCommand, Command
    from TradeEngine.GlobleConf import SysWidget, StrategyWidget, Shares
    from TradeEngine.MonitorClient import Monitor
    import traceback
    import json

    def get_shares_of_strategy(tid, strategy):
        try:
            shares = StrategyWidget.get_shares_mgr(strategy).get_dict_shares()
            account = StrategyWidget.get_account_mgr(strategy)
            share_list = []
            for los in shares:
                if los == Shares.Long:
                    los_str = 'buy'
                else:
                    los_str = 'sell'
                for instrument in shares[los]:
                    volume, price = shares[los][instrument]
                    if volume != 0:
                        position_profit = account.get_instrument_position_profit(los, instrument)
                        last_price = SysWidget.get_tick_data().get(instrument).DayClose
                        share_list.append(
                            [instrument, los_str, volume, '%2.2f' % price, '%2.2f' % last_price,
                             '%2.2f' % position_profit])
            return share_list
        except:
            Monitor.get_server_log('GetPosition').ERR(strategy, traceback.format_exc())

    def write_to_redis():
        redis = SysWidget.get_redis_reader()
        for strategy in StrategyWidget.SHARES:
            redis.hset('MONITOR.POSITION', strategy, json.dumps(get_shares_of_strategy(None, strategy)))

    IntervalCommand(1, Command(target=write_to_redis), SysWidget.get_external_engine())
