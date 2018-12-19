import datetime
from TradeEngine.GlobleConf import Sys

interval = 1
close_time = datetime.time(15, 1, 0)
interests_record_time = close_time
account_interests_record_time = close_time
income_of_strategy_record_time = close_time
total_account_name = Sys.ServerApp

stage_interests_record_time = (
    datetime.time(10, 16, 00),
    datetime.time(11, 31, 00),
    datetime.time(15, 01, 00),
    datetime.time(2, 31, 00),
)


UpdateRemoteAccountWriter = None


def get_update_remote_account_writer():
    global UpdateRemoteAccountWriter
    if UpdateRemoteAccountWriter is None:
        from TradeEngine.TradeServer.InfoUpdater.UpdateRemoteAccountCommand.RedisWriter import RedisWriter
        UpdateRemoteAccountWriter = RedisWriter()
    return UpdateRemoteAccountWriter
