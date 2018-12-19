from AccountConf import *
from InsertArgsV import Shares, OffSet, TradeSide
from syswidget import SysWidget
from TradeEngine.OnBarDataStruct import *


def init_start_conf(publish_key, conf):
    import StartConf
    StartConf.RedisHost = conf['REDIS_HOST']
    StartConf.RedisPort = int(conf['REDIS_PORT'])
    StartConf.RedisDB = int(conf['REDIS_DB'])
    StartConf.PublishKey = publish_key
    StartConf.RemoteServiceHost = conf['REMOTE_HOST']
    StartConf.RemoteServicePort = int(conf['REMOTE_PORT'])
    StartConf.CTPTradeHost = conf['CTP_TRADE_HOST']
    StartConf.BrokerId = conf['BROKER_ID']
    StartConf.UserId = conf['USER_ID']
    StartConf.Password = conf['PASSWORD']


def init_account_conf(conf):
    import AccountConf
    import cPickle
    AccountConf.AccountConf['default'] = float(conf['ACCOUNT_START_CASH'])
    context = cPickle.loads(str(conf['BACK_TEST_DRAW_DOWN']))
    for key in context:
        AccountConf.BackTestDrawDown[key] = context[key]


def init_redis_key(conf):
    import RedisKey

    @classmethod
    def rt(*args, **kwargs):
        return str(conf['DATA_PUBLISH_KEY'])

    RedisKey.Publish.DataPre = rt


def show_msg():
    import StartConf
    import RedisKey
    return "\n======================================\n" \
           "PublishKey: {}\n" \
           "RedisHost: {}\n" \
           "RedisPort: {}\n" \
           "RedisDB: {}\n" \
           "RemoteServiceHost: {}\n" \
           "RemoteServicePort: {}\n" \
           "Broker: {}\n" \
           "User: {}\n" \
           "MinDataKeyPrefix: {}\n" \
           "======================================\n".format(
        StartConf.PublishKey, StartConf.RedisHost, StartConf.RedisPort, StartConf.RedisDB, StartConf.RemoteServiceHost,
        StartConf.RemoteServicePort, StartConf.BrokerId, StartConf.UserId, RedisKey.Publish.DataPre())


def init_conf(publish_key):
    from Tables import ConfTable
    conf = ConfTable.create().get_conf(publish_key)
    init_start_conf(publish_key, conf)
    init_account_conf(conf)
    init_redis_key(conf)
    import Sys
    Sys.sys_config_init()
