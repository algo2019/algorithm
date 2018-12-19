# -*- coding:utf-8 -*-
import BaseAction
from dataBaseAPI.confMaker.dataConf import Maker
import aly
import datetime


class data(BaseAction.base):
    def __init__(self, dataBaseAdapter):
        BaseAction.base.__init__(self, dataBaseAdapter)
        self.__db = self.getDBA().getDataBase('gta')
        self.__ct = CTTABLE
        self.__dbnt = {
            'daily': {
                'stk': self.__db.getStockDaily,
                'idx': self.__db.getIdxDaily,
                'fut': self.__db.getFutDaily,
                'ffut': self.__db.getFFutDaily,
            },
            'min': {
                'stk': self.__db.getStockIdxMin,
                'idx': self.__db.getStockIdxMin,
                'fut': self.__db.getFutMin,
                'ffut': self.__db.getFFutMin,
            },
        }
        self.__dateFormator = aly.getDateFormator()

    def __fields__(self, fields, ctName):
        rtList = []
        fields = aly.getStr(fields)
        for field in fields.split(','):
            if self.__ct[ctName].get(field.lower()):
                rtList.append(self.__ct[ctName][field.lower()])
            else:
                rtList.append(field)
        return ','.join(rtList)

    def getDaily(self, maker):
        rt = []
        _fields = maker.getFields()
        for typeStr in maker.getMarketCode():
            _tmpCodeMarket = self.__code_market__(maker.getMarketCode(typeStr))
            maker.setType(typeStr)
            maker.setCode(_tmpCodeMarket[0])
            maker.setMarket(_tmpCodeMarket[1])
            maker.setFields(self.__fields__(_fields, 'daily%s' % (typeStr)))
            rt += maker.rtCodeRecognize(self.__dbnt['daily'][typeStr](maker.get()))
        maker.setFields(_fields)
        return rt

    def getMin(self, maker):
        rt = []
        marketCode = None
        # 添加 volume ，为了筛掉 volume 为 0 的部分
        # tfield = aly.getList(maker.getFields())
        # tfield.append('volume')
        # maker.setFields(tfield)
        _fields = maker.getFields()

        for typeStr in maker.getMarketCode():
            _tmpCodeMarket = self.__code_market__(maker.getMarketCode(typeStr))
            maker.setType(typeStr)
            maker.setCode(_tmpCodeMarket[0])
            maker.setMarket(_tmpCodeMarket[1])
            if typeStr in ['stk', 'idx']:
                marketCode = {'SH': [], 'SZ': []}
                for i in range(len(maker.getMarket())):
                    marketCode[maker.getMarket()[i]].append(maker.getCode()[i])
            if typeStr in ['ffut', 'fut']:
                maker.setFields(self.__fields__(_fields, 'min%s' % (typeStr)))
                tmp = self.__dbnt['min'][typeStr](maker.get())
                if maker.getFields() == 'OPENPX,HIGHPX,LOWPX,LASTPX,MINQTY' and maker.getPeriod() != '01':
                    rt += maker.rtBackTest(tmp)
                else:
                    rt += maker.rtCodeRecognize(tmp)
        if marketCode:
            for market in marketCode:
                maker.setGroupMarket(market)
                maker.setMarket([market for i in range(len(maker.getCode()))])
                maker.setFields(self.__fields__(_fields, 'minstk'))
                rt += maker.rtCodeRecognize(self.__dbnt['min']['stk'](maker.get()))

        maker.setFields(_fields)
        # 删除最后的 volume
        return rt

    def action(self, conf):
        maker = Maker(conf)
        if maker.getPeriod() == '1d':
            rt = self.getDaily(maker)
        else:
            rt = self.getMin(maker)
        return rt


CTTABLE = {
    'dailyidx': {
        'pre_close': 'LATESTCLOSE',
        'open': 'OPENPRICE',
        'high': 'HIGHPRICE',
        'low': 'LOWPRICE',
        'close': 'CLOSEPRICE',
        'volume': 'VOLUME',
        'amt': 'AMOUNT',
        'chg': 'CHANGE',
        'pct_chg': 'CHANGERATIO',
        'limitup': 'LIMITUP',
        'limitdown': 'LIMITDOWN',
    },
    'dailystk': {
        'pre_close': 'LATESTCLOSE',
        'open': 'OPENPRICE',
        'high': 'HIGHPRICE',
        'low': 'LOWPRICE',
        'close': 'CLOSEPRICE',
        'volume': 'VOLUME',
        'amt': 'AMOUNT',
        'chg': 'CHANGE',
        'pct_chg': 'CHANGERATIO',
        'swing': 'AMPLITUDE',
        'vwap': 'AVGPRICE',
        'turn': 'TURNOVERRATE1',
        'free_turn': 'TURNOVERRATE2',
        'lastradeday_s': 'DISTANCE',
        'last_trade_day': 'LATESTTADINGDATE',
        'rel_ipo_chg': 'RELATIVEIPOCHANGE',
        'rel_ipo_pct_chg': 'RELATIVEIPOCHANGERATIO',
        'trade_status': 'STATECODE',
        'maxup': 'LIMITUP',
        'maxdown': 'LIMITDOWN',
    },
    'minstk': {
        'open': 'STARTPRC',
        'high': 'HIGHPRC',
        'low': 'LOWPRC',
        'close': 'ENDPRC',
        'volume': 'MINTQ',
        'amt': 'MINTM',
    },
    'minffut': {
        'open': 'OPNPRC',
        'high': 'HIPRC',
        'low': 'LOPRC',
        'close': 'CLSPRC',
        'volume': 'MINTQ',
        'amt': 'MINTM',
    },
    'minfut': {
        'open': 'OPENPX',
        'high': 'HIGHPX',
        'low': 'LOWPX',
        'close': 'LASTPX',
        'volume': 'MINQTY',
        'amt': 'TURNOVER',
        'oi': 'OPENINTS',
    },
}
CTTABLE['dailyffut'] = CTTABLE['dailystk']
CTTABLE['dailyfut'] = CTTABLE['dailystk']
