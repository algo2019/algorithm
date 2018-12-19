import datetime

from Update_MFL1_from_Wind import DBOpr
from tools import get_exchange_id
from dataBaseAPI import dataBaseClient
from dataServer.tools import format_to_datetime

d = dataBaseClient.Client()
d.start()

from dataServer import dataServer
w = dataServer('10.2.53.13')
w.start()

start = datetime.datetime(2017, 02, 14, 9, 55)
end = datetime.datetime(2017, 02, 14, 10, 9)
cur = start

while cur < end:
    tn = cur + datetime.timedelta(minutes=1)
    tp = cur - datetime.timedelta(minutes=1)
    print 'new {} - {} - {}'.format(cur, tn, end)
    conf = {
        'dataName': 'sql',
        'dataBaseName': 'gta_mfl1_trdmin_201702',
        'sql': "select CONTRACTID from mfl1_trdmin01_201702 where tdatetime >= '{}' and tdatetime < '{}'".format(tp, cur)
    }
    i59 = set(map(lambda x: '{}.{}'.format(x[0], get_exchange_id(x[0])), d.wmm(conf)))
    conf = {
        'dataName': 'sql',
        'dataBaseName': 'gta_mfl1_trdmin_201702',
        'sql': "select CONTRACTID from mfl1_trdmin01_201702 where tdatetime >= '{}' and tdatetime < '{}'".format(cur, tn)
    }
    i00 = set(map(lambda x: '{}.{}'.format(x[0], get_exchange_id(x[0])), d.wmm(conf)))
    codes = list(i59 - i00)
    print 'per : {} cur : {} update : {}'.format(len(i59), len(i00), len(codes))
    if len(codes) > 0:
        for code in codes:
            print 'wsi {} - {}'.format(tp, cur)
            res = w.wsi(code, 'open,close,high,low,chg,pct_chg,oi,volume,amt', tp, cur)
            if res.ErrorCode != 0:
                print code, cur, res.Data
                continue
            print 'res', res.Times
            res.Times[0] = cur
            # DBOpr.delete(code.split('.')[0], format_to_datetime('{} 15:00:00'.format(cur)))
            DBOpr.insert(res)

    cur = tn