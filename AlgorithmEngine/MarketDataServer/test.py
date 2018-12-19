def debug():
    import tools
    import datetime
    from Common.CommonLogServer import mlogging
    mlogging.Conf.DEBUG = True
    last_tradingday = None

    def get_real_trading_date_time(data):
        global last_tradingday
        rt = tools.format_to_datetime('{} {}'.format(data['TradingDay'], data['UpdateTime']))
        if data['UpdateTime'] < '16:00:00':
            last_tradingday = data['TradingDay']
            return rt
        else:
            if last_tradingday is None:
                last_tradingday = str((rt - datetime.timedelta(days=1)).date())
            return tools.format_to_datetime('{} {}'.format(last_tradingday, data['UpdateTime']))

    from MarketDataService import ZeroProcessor
    ZeroProcessor.get_real_trading_date_time = staticmethod(get_real_trading_date_time)


import time
from Common.Event import Event
from MarketDataServer import mkdata_tools
from MarketDataService import TickService

from Common.PubSubAdapter.RedisPubSub import RedisPubSub
class RedisPS(RedisPubSub):
    e = Event()

    def __init__(self, *args, **kwargs):
        super(RedisPS, self).__init__(*args, **kwargs)
        self.last_tick = None

    def publish(self, key, msg):
        if key.startswith('test.llll.01'):
            print key, mkdata_tools.get_dict_data(msg)['dateTime']

    # def subscribe(self, keys, handler):
    #     self.e.subscribe(handler)
    #
    # def start(self):
    #     with open('bu1706.data', 'r') as f:
    #         for l in f.xreadlines():
    #             self.e.emit({'data': '{}|Turnover#{}'.format(l.strip().split()[1], 0)})


#
# import Conf
#
# Conf._PS = RedisPS('10.4.27.181', 6379)
# Conf.MKDATA_KEY = 'CTP.MKDATA.*'
# Conf._PK = 'tttt.minData'
# debug()
#
# ts = TickService()
# ts.start()
# Conf._PS.start()
#
# while 1:
#     time.sleep(1)
