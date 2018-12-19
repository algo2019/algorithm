# -*- coding:utf-8 -*-
import datetime

import Conf
import mkdata_tools
from Common.CommonLogServer.RedisLogService import PublishLogCommand
from Common.Event import Event
from tools import format_to_datetime as format_dt
import time


def get_publish_name(period='*', instrument_id='*'):
    return '%s.%s' % (get_event_name(period), instrument_id)


def get_event_name(period='*'):
    return '%s.%s' % (Conf.get_pk_pre(), period)


def get_bar_date_time(period_int, date_time):
    dt_start_date_time = datetime.datetime(date_time.year,
                                           date_time.month,
                                           date_time.day,
                                           date_time.hour,
                                           (date_time.minute / period_int) * period_int)
    return dt_start_date_time + datetime.timedelta(minutes=period_int)


class Bar(object):
    def __init__(self, period, bar, last_info):
        self.low = self.high = self.open = bar['close']
        self.last_volume = last_info['volume']
        self.last_turnover = last_info['turnover']
        self.last_bar = bar
        self.period = period
        self.end = get_bar_date_time(int(self.period), format_dt(bar['dateTime']))
        self.send_end = self.end
        self.published = False
        self.special_bar_init()

    def special_bar_init(self):
        # 开盘bar合并到第一个bar中
        if self.end.time() in {datetime.time(21), datetime.time(9)}:
            self.end += datetime.timedelta(minutes=int(self.period))
            self.send_end = self.end

        # 停盘Bar提前发送
        if self.end.time() in Conf.end_times:
            self.send_end = self.end - datetime.timedelta(seconds=Conf.advance_time)

    def process(self, data):
        last = data['close']
        if self.low > last:
            self.low = last
        if self.high < last:
            self.high = last
        self.last_bar = data

    def dict(self):
        rt = {'high': self.high,
              'low': self.low,
              'open': self.open,
              'volume': int(self.last_bar['Volume']) - self.last_volume,
              'turnover': float(self.last_bar['Turnover']) - self.last_turnover,
              'period': self.period,
              'dateTime': self.end, }
        return dict(self.last_bar, **rt)

    def __str__(self):
        d = self.dict()
        return '|'.join(('{}#{}'.format(key, d[key]) for key in d))


class logger(object):
    engine = None
    def __init__(self, logger_name, sys_name, source, engine=None):
        self.logger_name = logger_name
        self.sys_name = sys_name
        self.source = source
        if logger.engine is None:
            if engine is None:
                from Common.AtTimeObjectEngine import ThreadEngine
                logger.engine = ThreadEngine()
                logger.engine.start()
            else:
                logger.engine = engine

    def debug(self, msg):
        self.engine.add_command(PublishLogCommand(self.sys_name, self.logger_name, 'Main', 'DEBUG', self.source, msg))

    def error(self, msg):
        self.engine.add_command(PublishLogCommand(self.sys_name, self.logger_name, 'Main', 'ERR', self.source, msg))

    def info(self, msg):
        self.engine.add_command(PublishLogCommand(self.sys_name, self.logger_name, 'Main', 'INFO', self.source, msg))

    def warn(self, msg):
        self.engine.add_command(PublishLogCommand(self.sys_name, self.logger_name, 'Main', 'WARN', self.source, msg))

class Processor(object):
    def __init__(self, instrument, period):
        self.instrument = instrument
        self.period = period
        self.bar = None
        self.ps = Conf.get_ps()
        self.logger = logger('{}.{}'.format(self.instrument, self.period), Conf.SYSTEM_NAME, 'Processor')
        self.__last_info = {'volume': 0, 'turnover': 0}

    def filter(self):
        if self.bar.published:
            return False
        self.bar.published = True

        # 交易时间段之外的Bar
        if datetime.time(15) < self.bar.end.time() < datetime.time(21, 1) or \
                                datetime.time(2, 30) < self.bar.end.time() < datetime.time(9, 1):
            self.logger.debug('UnExcepted Bar {}.{}.{}'.format(
                self.instrument, self.period, self.bar.end))
            return False

        # 当前tick与发送的Bar时间不能超过60分钟，否则判为无效(会过滤掉不活跃合约)
        if self.bar.last_bar['dateTime'] - datetime.timedelta(minutes=60) > self.bar.end:
            self.logger.debug('LastTick is {} on Bar {}.{}.{}'.format(
                self.bar.last_bar['dateTime'], self.instrument, self.period, self.bar.end))
            return False

        return True

    def publish(self):
        if not self.filter():
            return
        self.ps.publish(get_publish_name(self.bar.period, self.instrument),
                        '{}|MINSend#{:f}'.format(str(self.bar), time.time()))

    def process(self, data):
        if self.bar is None:
            self.bar = Bar(self.period, data, self.__last_info)
        elif data['dateTime'] < self.bar.last_bar['dateTime']:
            self.logger.error('Datetime is lower than last:{} now:{}'.format(
                self.bar.last_bar['dateTime'], data['dateTime']))
        else:
            # 将最新Tick归入上一Bar中
            self.bar.process(data)
            if data['dateTime'] < self.bar.end:
                if data['dateTime'] >= self.bar.send_end:
                    self.publish()
            else:
                self.publish()
                self.__last_info['volume'] = int(data['Volume'])
                self.__last_info['turnover'] = float(data['Turnover'])
                self.bar = None


class ZeroProcessor(object):
    def __init__(self):
        self.__period = '00'
        self.tick_data_event = Event()
        self.__info = {}
        self.ps = Conf.get_ps()

    @staticmethod
    def get_real_trading_date_time(data):
        update_time = data['UpdateTime']
        now = datetime.datetime.now()
        trade_time = format_dt(update_time, date=False)
        if trade_time.hour < 16 < now.hour:
            real_trade_date = (now + datetime.timedelta(days=1)).date()
        elif trade_time.hour > 16 > now.hour:
            real_trade_date = (now + datetime.timedelta(days=-1)).date()
        else:
            real_trade_date = now.date()
        return format_dt('%s %s' % (str(real_trade_date), update_time), ms=True)

    def _publish(self, data):
        pub_list = []
        pub_key = get_publish_name(self.__period, data['InstrumentID'])
        for key in data:
            pub_list.append('%s#%s' % (key, data[key]))
        self.ps.publish(pub_key, '|'.join(pub_list))

    def update(self, str_data):
        str_data['data'] = '{}|MINStart#{:f}'.format(str_data['data'], time.time())
        data = mkdata_tools.get_dict_data(str_data)
        data['close'] = float(data['LastPrice'])
        data['dateTime'] = self.get_real_trading_date_time(data)
        data['realDate'] = datetime.datetime.now().date()
        data['Volume'] = data['Volume']
        data['volume'] = 0
        data['high'] = data['close']
        data['low'] = data['close']
        data['open'] = data['close']
        # 未实现
        data['Turnover'] = 0
        data['ExchangeID'] = mkdata_tools.get_exchange_id(data['InstrumentID'])
        data['period'] = '00'
        self._publish(data)
        self.tick_data_event.emit(data)


class TickService(object):
    def __init__(self):
        self.__zero_processor = ZeroProcessor()
        self.processors = {}
        self.logger = logger('TickService', Conf.SYSTEM_NAME, 'TickService')
        self.logger.info('init ready!')

    def start(self):
        self.__zero_processor.tick_data_event.subscribe(self.groups)
        Conf.get_ps().subscribe(Conf.MKDATA_KEY, self.__zero_processor.update)
        self.logger.info('start')

    def groups(self, d):
        processors = self.processors.get(d['InstrumentID'])
        if processors is None:
            instrument = d['InstrumentID']
            processors = [Processor(instrument, period) for period in Conf.PERIODS]
            self.processors[instrument] = processors
        for processor in processors:
            processor.process(d)

    def reset(self):
        self.processors = {}
        self.logger.info('reset ready')

    @property
    def tick_event(self):
        return self.__zero_processor.tick_data_event
