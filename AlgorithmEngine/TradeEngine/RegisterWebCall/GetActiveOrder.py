def call():
    from TradeEngine.GlobleConf import SysWidget
    from TradeEngine.GlobleConf.RedisKey import DB
    from TradeEngine.GlobleConf.StrategyWidget import ACCOUNT
    from Common.Command import Command, IntervalCommand
    import json

    def update_active_order(active_order_list):
        order_dict = {strategy: [] for strategy in ACCOUNT}
        for order in active_order_list:
            order_dict[order.strategy_name].append([str(order.datetime)[:19], order.instrument, order.offset, order.trade_side,
                           order.volume, '%2.2f' % order.price, order.filled_volume, '%2.2f' % order.filled_price,
                           order.state.string])

        if len(order_dict):
            r = SysWidget.get_redis_reader()
            for strategy in order_dict:
                r.hset(DB.Monitor.ActiveOrder(), strategy, json.dumps(order_dict[strategy]))

    IntervalCommand(1, Command(target=SysWidget.get_active_order_list().handler, args=(update_active_order,)),
                    SysWidget.get_external_engine())
