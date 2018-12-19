# coding=utf-8
import datetime
from decimal import Decimal
from tools import format_to_datetime as fdt
from Common.Dao import DBDataDao


class DataSet(object):
    """
    仿照Wind的输出对象
    """

    def __init__(self):
        self.ErrorCode = None
        self.Codes = None
        self.Fields = None
        self.Times = None
        self.Data = None

    def __str__(self):
        _tmp = map(str, self.Times)
        return '.ErrorCode = ' + str(self.ErrorCode) + '.Codes = ' + str(self.Codes) + '.Fields = ' + \
               str(self.Fields) + '.Times = ' + str(_tmp) + '.Data = ' + str(self.Data)


class Dataserver(object):
    """
    仿dataServer接口对象
    """

    def __init__(self, *args, **kwargs):
        self._db = DBDataDao()

    def start(self, p=None):
        pass

    def stop(self):
        pass

    @staticmethod
    def _to_str(str_or_list):
        if isinstance(str_or_list, basestring):
            return str_or_list
        return ','.join(str_or_list)

    @staticmethod
    def _to_list(str_or_list):
        if isinstance(str_or_list, basestring):
            return str_or_list.split(',')
        return str_or_list

    @staticmethod
    def _date_to_datetime(_list, indexs):
        _list = list(_list)
        for i in range(len(_list)):
            l = list(_list[i])
            for index in indexs:
                l[index] = datetime.datetime.combine(l[index], datetime.time(0))
            _list[i] = l
        return _list

    @staticmethod
    def _start_end(config):
        if config.get('start') is None:
            raise Exception('start can not be none!')
        if config.get('end') is None:
            config['end'] = datetime.datetime.now()
        return fdt(config['start'], time=False), fdt(config['end'], time=False)

    def _day(self, config):
        code = self._to_str(config['code'])
        fields = self._to_list(config.get('fields', []))
        for i in range(len(fields)):
            if _field_convert_table.get(fields[i]) is not None:
                fields[i] = _field_convert_table.get(fields[i])

        start, end = self._start_end(config)
        rt = self._date_to_datetime(self._db.day(code, start, end, self._to_str(fields)), [0])
        for l in rt:
            for i in xrange(2, len(l)):
                if isinstance(l[i], Decimal):
                    l[i] = float(l[i])
        return rt

    def _dom(self, config):
        start, end = self._start_end(config)
        afterday = config.get('afterday', 0)
        beforday = config.get('beforday') or config.get('beforeday', 0)
        commodity = self._to_list(config.get('commodity'))
        rt = []
        for symbol in commodity:
            rt += self._date_to_datetime(self._db.main_contract(symbol, start, end, beforday, afterday), [2, 3])
        return rt

    def wmm(self, config):
        """
        仿dataServer接口仅支持domInfo 及 data(period=1d)
        :param config: 参数规则等同dataServer.wmm
        :return: 
        """
        if config.get('dataName') == 'data':
            period = config.get('period')
            if period is None or period == '1d':
                return self._day(config)

        if config.get('dataName') == 'domInfo':
            return self._dom(config)

    def tdays(self, *argv):
        d = DataSet()
        print argv
        times = map(fdt, self._db.tdays(*argv))
        d.Times = times
        d.Data = [times]
        return d

    def tdaysoffset(self, *argv):
        d = DataSet()
        times = fdt(self._db.tdaysoffset(*argv))
        d.Times = [times]
        d.Data = [[times]]
        return d


_field_convert_table = {
    'pre_close': 'PERCLOSEPRICE',
    'open': 'OPENPRICE',
    'high': 'HIGHPRICE',
    'low': 'LOWPRICE',
    'close': 'CLOSEPRICE',
    'volume': 'VOLUME',
    'amt': 'AMOUNT',
    'chg': 'CHG',
    'pct_chg': 'CHGRT',
}

dataServer = Dataserver
d = Dataserver()

if __name__ == '__main__':

    for line in d.wmm({
        'fields': 'close',
        'dataName': 'data',
        'start': datetime.datetime(2017, 5, 1),
        'end': datetime.datetime(2017, 12, 22),
        'code': 'ag1709'
    }):
        print line
