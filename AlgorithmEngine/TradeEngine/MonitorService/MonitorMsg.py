from TradeEngine.GlobleConf import StrategyWidget


class HeartBeatMsg(object):
    def __init__(self, monitor_server, data):
        self.monitor_server = monitor_server
        self.data = data

    def execute(self):
        strategy = self.data['channel'].split('.')[2]
        StrategyWidget.get_account_mgr(strategy)
        self.monitor_server.set_heart_beat(strategy)


LEVEL_CLASS_TABLE = {
    'HEARTBEAT': HeartBeatMsg,
}


def get_msg(monitor_server, data):
    level = data['channel'].split('.')[1]
    return LEVEL_CLASS_TABLE.get(level)(monitor_server, data)

