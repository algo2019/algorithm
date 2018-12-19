# -*- coding:utf-8 -*-
import dataServer
from dataBaseAPI import dataBaseClient
from NewDataBaseAPI import Adapter as NewDataBaseClient
import datetime
from pprint import pprint


def testWsd(w):
    if 1:
        for rt in [
            w.wsd('000001.SZ,000001.SH,IF1405.CFE,IF1606.DE,A1405.CFE', 'close', '2014-01-01', '20140502'),
            w.wsd('000001.SZ', 'Close,open', '20110401', '20110410'),
        ]:
            if rt.ErrorCode != 0:
                rt._print()
                raise Exception('err')
    print 'wsd ok'


def testWsi(w):
    if 1:
        for rt in [
            w.wsi('600000.SH', 'close,open', '2014-09-01', '20140902', 'period=60'),
            w.wsi('IF1405.CFE', 'close', '2014-01-01', '20140502', 'period=60'),
            w.wsi('IF1405.CFE,IF1606.DE,600000.SH,000001.SH,000001.SZ,A1405.CFE,A1406.CFE', 'close', '2014-01-01',
                  '20140502', 'period=60'),
        ]:
            if rt.ErrorCode != 0:
                rt._print()
                raise Exception('err')
    print 'wsi ok'


def testAll(w):
    if 1:
        testList = []
        # 分红数据测试
        testList.append({'dataName': 'divident', 'code': '000001.SH,000001.SZ'})
        # 股票日线测试
        testList.append(
            {'dataName': 'data', 'code': '000001.SZ,600000.SH,000001.SH', 'fields': 'close,open', 'start': '20140910',
             'end': '20140911', 'period': '1d', 'adj': '0'})
        # 股票分钟级测试
        testList.append(
            {'dataName': 'data', 'code': '000001.SZ,600000.SH,000001.SH', 'fields': 'close,open', 'start': '20140910',
             'end': '20140911', 'period': '60m', 'adj': '0'})
        # 股指期货日线测试
        testList.append({'dataName': 'data', 'code': 'IF1605.CFE,IF1604', 'fields': 'close,open', 'start': '20140110',
                         'period': '1d'})
        # 股指期货分钟级测试
        testList.append({'dataName': 'data', 'code': 'IF1405.CFE,IF1404', 'fields': 'close,open', 'start': '20140110',
                         'end': '20140710', 'period': '60m'})
        # 商品期货日线测试
        testList.append(
            {'dataName': 'data', 'code': 'AA9801', 'fields': 'close,open', 'start': '19900110', 'period': '1d'})
        # 商品期货分钟级测试
        testList.append(
            {'dataName': 'data', 'code': 'A1405', 'fields': 'close,open', 'start': '20140401', 'end': '20140502',
             'period': '60m'})
        # 混合品种日线测试
        testList.append({'dataName': 'data', 'code': 'A1405,IF1405,000001.SH,000001.SZ', 'fields': 'close,open',
                         'start': '20140401', 'end': '20140502', 'period': '1d'})
        # 混合品种分钟测试
        testList.append({'dataName': 'data', 'code': 'A1405,IF1405,000001.SH,000001.SZ', 'fields': 'close,open',
                         'start': '20140401', 'end': '20140502', 'period': '60m'})
        for conf in testList:
            rt = w.wmm(conf)
            try:
                if len(rt) == 0:
                    raise Exception('no res')
            except Exception, e:
                print conf
                print e
                return
        print 'testOver'


def testDomInfo(w):
    import datetime
    conf = {
        'dataName': 'domInfo',
        'start': datetime.datetime(2017, 01, 1),
        'end': datetime.datetime(2018, 12, 22),
        'afterday': 0,
        'beforday': 0,
        'commodity': ['ag'],
    }
    res = w.wmm(conf)
    for line in res:
        print line
    print 'domInfo', len(res)


def testFuts(w):
    if 1:
        conf = {
            'dataName': 'futs',
            'futs': [
                [u'AL1502', 60 * 60, datetime.datetime(2014, 10, 24, 0, 0), datetime.datetime(2014, 12, 15, 0, 0)],
                [u'AL1503', 60, datetime.datetime(2014, 11, 3, 0, 0), datetime.datetime(2014, 12, 23, 0, 0)],
                [u'B1405', 60, datetime.datetime(2014, 12, 22, 0, 0), datetime.datetime(2014, 4, 14, 0, 0)],
                [u'B1407', 60, datetime.datetime(2014, 3, 3, 0, 0), datetime.datetime(2014, 4, 29, 0, 0)],
                [u'B1409', 60, datetime.datetime(2014, 3, 18, 0, 0), datetime.datetime(2014, 5, 11, 0, 0)],
                [u'B1411', 60, datetime.datetime(2014, 9, 2, 0, 0), datetime.datetime(2014, 10, 31, 0, 0)],
                [u'B1501', 60, datetime.datetime(2014, 8, 12, 0, 0), datetime.datetime(2014, 10, 21, 0, 0)],
            ],
            'fields': 'close,open',
        }
        res = w.wmm(conf)
        print 'futs min', len(res)

        conf = {
            'dataName': 'futs',
            'futs': [
                [u'AL1502', 60 * 60 * 24, '20141024', '20141215'],
                [u'AL1503', 60 * 60 * 24, '20141103', datetime.datetime(2014, 12, 23, 0, 0)],
            ],
            'fields': 'close,open',
        }
        res = w.wmm(conf)
        print 'futs daily', len(res)


def testTdays(w):
    res = w.tdays('1990-01-01', '2015-01-01')
    if res.ErrorCode != 0:
        raise Exception(str(res.Data[0]))
    pprint(res.Data[0][:30])
    print 'tdays', len(res.Data[0])


def test(db1):
    conf = {
        'dataName': 'data',
        'code': 'al1707',
        'fields': 'open,high,low,close,volume',
        'start': '20170509 16:00:00',  # 可选，默认为当前日期
        'end': '20170510 16:00:00',  # 可选，默认为当前日期
        'period': '1m',  # 可选，默认为 1d，支持 1d 1m 5m 10m 15m 30m 60m
        # 'includeend': False,
    }
    res = db1.wmm(conf)
    for line in res:
        print line, ','


#
if __name__ == '__main__':
    # w = dataBaseClient.Client()
    # w = dataServer.dataServer('127.0.0.1')
    # w = NewDataBaseClient()
    from dataServer import Conf

    Conf.DB_PATH = None
    Conf.CACHE = False

    w = dataServer.dataServer('10.4.37.198')
    # w.port = 60000
    w.start()
    try:
        testDomInfo(w)
        # testFuts(w)
        # testWsd(w)
        # testWsi(w)
        # testAll(w)
        # testTdays(w)
        # test(w)
        # print w.tdaysoffset(1).Data[0][0]
    finally:
        try:
            w.stop()
        except:
            pass
