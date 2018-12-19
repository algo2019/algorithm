import datetime
from DBApi.Tables import DailyDataTable, DomInfoTable, TradingDateTable, MinDataTable
from DBApi import Conf, tools


class WindSet(object):
    def __init__(self):
        self.ErrorCode = 0
        self.Times = []
        self.Data = []

    def __str__(self):
        return '.ErrorCode:{}\n.Times:{}\n.Data:{}'.format(self.ErrorCode, self.Times, self.Data)


class Client(object):
    def __init__(self, path=None):
        if path is not None:
            Conf.DB_PATH = path
        self._mdt = MinDataTable()
        self._dit = DomInfoTable()
        self._tdt = TradingDateTable()
        self._ddt = DailyDataTable()

    def start(self):
        self._mdt.open()
        self._dit.open()
        self._tdt.open()
        self._ddt.open()

    def stop(self):
        self._mdt.close()
        self._dit.close()
        self._tdt.close()
        self._ddt.close()

    def tdays(self, start, end=None):
        end = end or datetime.datetime.now()
        rt = WindSet()
        rt.Times = map(tools.format_to_datetime, self._tdt.tdays(start, end))
        rt.Data.append(rt.Times)
        return rt

    def tdaysoffset(self, offset, dt=None):
        dt = dt or datetime.datetime.now()
        rt = WindSet()
        rt.Times = [tools.format_to_datetime(self._tdt.tdaysoffset(offset, dt))]
        rt.Data.append(rt.Times)
        return rt

    def wmm(self, conf):
        if conf['dataName'] == 'domInfo':
            return self._dom_info(conf)
        if conf['dataName'] == 'data' and conf['period'] == '1d':
            return self._daily(conf)
        if conf['dataName'] == 'data' and conf['period'] != '1d':
            return self._min(conf)
        else:
            raise Exception('not support this conf!' + str(conf))

    def _dom_info(self, conf):
        rt = []
        conf['start'] = conf['start']
        conf['end'] = conf.get('end', datetime.datetime.now())
        for commodity in conf['commodity']:
            for line in self._dit.select(commodity, conf['start'], conf['end'], conf.get('beforday', 0),
                                         conf.get('afterday', 0)):
                rt.append([line[0], tools.format_to_datetime(line[1]), tools.format_to_datetime(line[2])])
        return rt

    def _daily(self, conf):
        if conf.get('includeend', False):
            conf['end'] = conf['end'] + datetime.timedelta(days=1)
        return self._ddt.select(conf['code'], conf['start'], conf.get('end', datetime.datetime.now()), conf['fields'])

    def _min(self, conf):
        conf['end'] = conf.get('end', datetime.datetime.now())
        if conf.get('tradingday'):
            conf['start'] = tools.format_to_datetime('{} 20:00:00'.format(self._tdt.tdaysoffset(1, conf['start'])))
            conf['end'] = datetime.datetime.combine(tools.format_to_datetime(conf['end'], time=False), datetime.time(20))
            if conf.get('includeend', False):
                conf['end'] = conf['end'] - datetime.timedelta(days=1)

        return self._mdt.select(conf['code'], conf['period'], conf['start'], conf['end'], conf['fields'])


if __name__ == '__main__':
    w = Client()
    w.start()
    conf = {
        'dataName': 'data',
        'start': '20151210 000000',
        'end': '20151231 235959',
        'code': 'IF1601',
        'fields': 'open,high,low,close,volume',
        'period': '1m',
    }
    print w.wmm(conf)
