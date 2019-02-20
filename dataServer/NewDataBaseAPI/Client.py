import abc

import datetime
from decimal import Decimal
from xmlrpclib import ServerProxy

import tools
import Conf


class BaseClient(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_data(self, conf):
        raise NotImplementedError


class ControlClient(BaseClient):
    @abc.abstractmethod
    def add_client(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_client(self, *args, **kwargs):
        raise NotImplementedError


class TimeClientPreProcessingClient(ControlClient):
    def __init__(self):
        self._clients = {}

    def add_client(self, key, client):
        self._clients[key] = client

    def remove_client(self, key):
        self._clients.pop(key, None)

    def get_client(self, conf):
        try:
            return self._clients.get(conf.get('dataName'))
        except:
            raise Exception('TimeClientPreProcessingClient get client of {} error'.format(conf.get('dataName')))

    def before_action(self, conf):
        if conf['dataName'] == 'data':
            if conf['period'] in ('01', '05', '10', '15', '30', '1m', '5m', '10m', '15m', '30m'):
                conf['dataName'] = 'minData'
            elif conf['period'] == '1d':
                conf['dataName'] = 'dayData'
        if conf.get('tradingday'):
            ts_conf = {'dataName': 'tdaysoffset', 'offset': 1, 'datetime': conf['start']}
            start_date = self.get_client(ts_conf).get_data(ts_conf).date()
            if not conf.get('includeend', False):
                ts_conf = {'dataName': 'tdaysoffset', 'offset': 1, 'datetime': conf['end']}
                end_date = self.get_client(ts_conf).get_data(ts_conf).date()
                conf['end'] = end_date

            conf['start'] = tools.format_to_datetime('{} 20:00:00'.format(start_date))
            conf['end'] = datetime.datetime.combine(tools.format_to_datetime(conf['end'], time=False),
                                                    datetime.time(20))
        else:
            if conf.get('start'):
                conf['start'] = tools.format_to_datetime(conf['start'])
                if conf.get('end') is None:
                    conf['end'] = datetime.datetime.now()
                else:
                    conf['end'] = tools.format_to_datetime(conf['end'])
                if conf.get('includeend'):
                    conf['end'] += datetime.timedelta(minutes=1)
        conf.pop('includeend', None)
        conf.pop('tradingday', None)

    def get_data(self, conf):
        self.before_action(conf)
        return self.get_client(conf).get_data(conf)

    def __getattr__(self, item):
        return getattr(self.get_client({'dataName': 'other'}), item)


class TradingDaysClient(BaseClient):
    def tdaysoffset(self, offset, start):
        _len = max(abs(offset) * 2, 10)
        forword = True
        if offset < 0:
            forword = False
            offset = abs(offset)
        if not start:
            start = datetime.datetime.now().date()
        else:
            start = tools.format_to_datetime(start, time=False)

        while 1:
            _len += _len
            if forword:
                res = self.tdays(start - datetime.timedelta(days=_len),
                                 datetime.datetime.combine(start, datetime.time(1)))
            else:
                res = self.tdays(start, start + datetime.timedelta(days=_len))
            if len(res) > offset:
                if forword:
                    return res[-1 - offset]
                else:
                    return res[offset]

    def tdays(self, start, end):
        db = Conf.get_gta_db()
        rt = db.db_run_sql('GTA_QIA_QDB',
                           "SELECT CALENDARDATE FROM STK_CALENDARD WHERE EXCHANGECODE='SSE' AND ISOPEN='Y' "
                           "AND CALENDARDATE>='%s' AND CALENDARDATE<'%s' order by CALENDARDATE" % (
                               start, end))
        return map(lambda x: x[0], rt)

    def get_data(self, conf):
        if conf['dataName'] == 'tdaysoffset':
            return self.tdaysoffset(conf['offset'], conf.get('datetime'))
        elif conf['dataName'] == 'tdays':
            return self.tdays(conf['start'], conf['end'])


class TradeRecordClient(BaseClient):
    def __init__(self):
        from Common.Dao.DBDataDao import DBDataDao
        self._dao = DBDataDao()

    @staticmethod
    def _date_to_datetime(_list, indexs):
        _list = list(_list)
        for i in range(len(_list)):
            l = list(_list[i])
            for index in indexs:
                l[index] = datetime.datetime.combine(l[index], datetime.time(0))
            _list[i] = l
        return _list

    def main_contract(self, symbol, start, end, before, after):
        start = self._dao.tdaysoffset(before, start)
        end = self._dao.tdaysoffset(0 - after, end)
        symbol_list = symbol.split(',')
        return self._date_to_datetime([[s + '0', start, end] for s in symbol_list], [1, 2])

    def get_data(self, conf):
        if conf['dataName'] == 'tdaysoffset':
            return self._dao.tdaysoffset(conf['offset'], conf.get('datetime'))
        elif conf['dataName'] == 'tdays':
            return self._dao.tdays(conf['start'], conf['end'])
        elif conf['dataName'] == 'domInfo':
            return self.main_contract(conf['commodity'], conf['start'], conf['end'], conf['beforday'], conf['afterday'])
        elif conf['dataName'] == 'dayData':
            rt = self._dao.day(conf['code'], conf['start'], conf.get('end'), conf.get('fields'))
            rt = self._date_to_datetime(rt, [0])
            for l in rt:
                for i in xrange(2, len(l)):
                    if isinstance(l[i], Decimal):
                        l[i] = float(l[i])
            return rt


class MinDataAdapterClient(BaseClient):
    def __init__(self):
        self.proxy = ServerProxy("http://{}:{}/".format(Conf.MinDataService.Host, Conf.MinDataService.Port))

    def get_data(self, conf):
        if conf['dataName'] == 'minData':
            return self.proxy.wmm(conf)
