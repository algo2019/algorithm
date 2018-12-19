import datetime

SYSTEM_NAME = 'MarketDataService'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

MKDATA_KEY = 'CTP.MKDATA.*'


PERIODS = ('01', '05', '10', '15', '30')

_PK = None


try:
    import package_config
    import os
    if os.path.exists(package_config.config_file):
        with open(package_config.config_file) as f:
            import json
            config = json.load(f)
            REDIS_HOST = config['redis_host']
            REDIS_PORT = config['redis_port']
            MKDATA_KEY = config['market_data']['mk_data_key']
            _PK = config['market_data']['publish_key']
except Exception as e:
    print 'load config err:', str(e)


def get_pk_pre():
    if _PK is None:
        return 'test.llll'
    else:
        return _PK


_PS = None


def get_ps():
    global _PS
    if _PS is None:
        from Common.PubSubAdapter.RedisPubSub import RedisPubSub
        _PS = RedisPubSub(REDIS_HOST, REDIS_PORT)
    return _PS


advance_time = 10

end_times = {datetime.time(10, 15), datetime.time(11, 30),
             datetime.time(15), datetime.time(23), datetime.time(23, 30),
             datetime.time(1), datetime.time(2, 30)
             }

print SYSTEM_NAME
print 'REDIS_HOST', REDIS_HOST
print 'REDIS_PORT', REDIS_PORT
print 'MKDATA_KEY', MKDATA_KEY
print 'PUBLISH_KEY', _PK
