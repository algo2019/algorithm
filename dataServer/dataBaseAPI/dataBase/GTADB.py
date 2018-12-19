# -*- coding:utf-8 -*-

import dataBase
from datetime import datetime
from sqlBuilder import sqlBuilder
import sys
import copy

reload(sys)
sys.setdefaultencoding( "utf-8" )

def mym(date):
    return '%d%.2d'%(date.year,date.month)
def mymd(date):
    return '%d%.2d%.2d'%(date.year,date.month,date.day)
def mhm(date):
    return '%.2d%.2d'%(date.hour,date.minute)

class GTASqlBuilder(sqlBuilder):
    def buildDateTime(self,conf):
        if type(conf['dateName']) == list:
            whereDate = []
            dn = conf['dateName'][0]
            tn = conf['dateName'][1]
            if conf.get('start') and conf.get('end'):
                if conf['start'].date() == conf['end'].date():
                    whereDate.append(" %s='%s' and %s>='%s' and %s<'%s' "%
                        (dn,mymd(conf['start']),tn,mhm(conf['start']),tn,mhm(conf['end'])))
                else:
                    whereDate.append(" ((%s='%s' and %s>='%s') or (%s>'%s' and %s<'%s') or (%s='%s' and %s<='%s')) "%
                        (dn,mymd(conf['start']),tn,mhm(conf['start']),dn,mymd(conf['start']),dn,mymd(conf['end']),dn,mymd(conf['end']),tn,mhm(conf['end'])))
            elif conf.get('start'):
                whereDate.append("((%s='%s' and %s>='%s') or (%s>'%s'))"%
                    (dn,mymd(conf['start']),tn,mhm(conf['start']),dn,mymd(conf['start'])))
            elif conf.get('end'):
                whereDate.append("((%s='%s' and %s<'%s') or (%s<'%s'))"%
                    (dn,mymd(conf['end']),tn,mhm(conf['end']),dn,mymd(conf['end'])))
            return whereDate
        else:
            return sqlBuilder.buildDateTime(self,conf)
    def buildSelect(self,conf,fg=1):
        tmp = conf['dateName']
        if type(conf['dateName']) == list:
            conf['dateName'] = ','.join(conf['dateName'])
        rt = sqlBuilder.buildSelect(self,conf,fg)
        conf['dateName'] = tmp
        return rt
    def buildTableName(self,conf, date=None):
        if not date:
            date = conf['start']
        if conf.get('preTableName') and conf.get('period'):
            if conf['period'] not in (['01','05','10','15','30','60']):
                raise Exception('buildTableName period undefined:%s'%(conf['period']))
            return "%s%s_%s"%(conf['preTableName'],conf['period'],mym(date))
    def buildOthers(self,conf):
        tmp = conf['dateName']
        if type(tmp) == list:
            conf['dateName'] = ','.join(tmp)
        rt = sqlBuilder.buildOthers(self,conf)
        conf['dateName'] = tmp
        return rt
    def __save_futs_state__(self,conf):
        self.__state = {}
        if conf.get('code'):
            self.__state['code'] = conf['code']
            del conf['code']
        if conf.get('start'):
            self.__state['start'] = conf['start']
            del conf['start']
        if conf.get('end'):
            self.__state['end'] = conf['end']
            del conf['end']
    def __load_futs_state__(self,conf):
        for key in self.__state:
            conf[key] = self.__state[key]
    def __build_futs__(self,conf):
        if not conf.get('futs'):
            raise Exception('buildFuts need futs')
        self.__save_futs_state__(conf)
        cmdList = []
        for line in conf['futs']:
            cmdList.append(" (%s='%s' and %s>='%s' and %s<'%s') "%
                (conf['codeName'],line[0],conf['dateName'],line[2],conf['dateName'],line[3]))
        self.addOtherWhere(conf,'(%s)'%(' or '.join(cmdList)))
        rt = sqlBuilder.build(self,conf)
        self.__load_futs_state__(conf)
        return rt
    def build(self,conf):
        if conf.get('futs'):
            return self.__build_futs__(conf)
        else:
            return sqlBuilder.build(self,conf)
        


class GTADB(dataBase.sqlServerDataBase):
    def __init__(self, dbName='tempdb'):
        self.__HOST = '10.4.27.179'
        self.__PORT = 1433
        self.__USER, self.__PASSWD = self.defaultUser()
        self.__sql = GTASqlBuilder()
        dataBase.sqlServerDataBase.__init__(self,self.__HOST,self.__PORT,self.__USER,self.__PASSWD,dbName)
    def defaultUser(self):
        return 'research','rI2016'
    # GTA_QIA_QDB 中的日线数据
    def __GTA_QIA_QDB_QUOTATION__(self,conf):
        conf['dateName'] = 'TRADINGDATE'
        conf['codeName'] = 'SYMBOL'
        self.__sql.addOtherWhere(conf,"FILLING='0'")
        return self.dbRunSql('GTA_QIA_QDB',self.__sql.build(conf))
    # 从指数日线数据库中获取交易日期序列
    def __STK_CALENDARD__(self,conf):
        return self.dbRunSql('GTA_QIA_QDB',
            "SELECT CALENDARDATE FROM STK_CALENDARD WHERE EXCHANGECODE='SSE' AND ISOPEN='Y' AND CALENDARDATE>='%s' AND CALENDARDATE<'%s' order by CALENDARDATE"%(conf['start'],conf['end']))
    # 从分红信息表中获取分红信息
    def __STK_MKT_DIVIDENT__(self,conf):
        conf['tableName'] = 'STK_MKT_DIVIDENT'
        conf['fields'] = 'ExDividendDate,AllotmentPrice,AllotmentPerShare,DividentBT,DividentAT,BonusRatio,ConverSionRatio'
        conf['dateName'] = 'RecordDate'
        conf['codeName'] = 'SYMBOL'
        conf['orderBy'] = 'date'
        return self.dbRunSql('GTA_QIA_QDB',self.__sql.build(conf))
    # 获取指定日期的主力合约
    def __PUB_MAINCONTRACT__(self,conf):
        conf['tableName'] = 'PUB_MAINCONTRACT'
        conf['fields'] = 'SYMBOL'
        conf['codeName'] = 'UNDERLYINGASSETSCODE'
        conf['dateName'] = 'TRADINGDATE'
        conf['orderBy'] = 'UNDERLYINGASSETSCODE,TRADINGDATE'
        return self.dbRunSql('GTA_QIA_QDB',self.__sql.build(conf))
    # 股票日线不复权数据
    def __STK_MKT_QUOTATION__(self,conf):
        conf['tableName'] = 'STK_MKT_QUOTATION'
        return self.__GTA_QIA_QDB_QUOTATION__(conf)
    # 股票日线前复权数据
    def __STK_MKT_FWARDQUOTATION__(self,conf):
        conf['tableName'] = 'STK_MKT_FWARDQUOTATION'
        return self.__GTA_QIA_QDB_QUOTATION__(conf)
    # 股票日线后复权数据
    def __STK_MKT_BWARDQUOTATION__(self,conf):
        conf['tableName'] = 'STK_MKT_BWARDQUOTATION'
        return self.__GTA_QIA_QDB_QUOTATION__(conf)
    # 指数日线数据
    def __IDX_MKT_QUOTATION__(self,conf):
        conf['tableName'] = 'IDX_MKT_QUOTATION'
        return self.__GTA_QIA_QDB_QUOTATION__(conf)
    # 商品期货日线数据
    def __FUT_QUOTATIONHISTORY__(self,conf):
        conf['tableName'] = 'FUT_QUOTATIONHISTORY'
        return self.__GTA_QIA_QDB_QUOTATION__(conf)
    # 股指期货日线数据
    def __FFUT_QUOTATION__(self,conf):
        conf['tableName'] = 'FFUT_QUOTATION'
        return self.__GTA_QIA_QDB_QUOTATION__(conf)

    # 股票日线数据
    def getStockDaily(self,conf):
        if not conf.get('type') or conf['type'] != 'stk':
            raise Exception('GTADB getFFutMin conf type err')
        if conf['adj'] == '0':
            return self.__STK_MKT_QUOTATION__(conf)
        elif conf['adj'] == 'f':
            return self.__STK_MKT_FWARDQUOTATION__(conf)
        elif conf['adj'] == 'b':
            return self.__STK_MKT_BWARDQUOTATION__(conf)
        else:
            raise Exception('GTADB getStockDaily adj undefine:%s'%(conf['adj']))
    # 指数日线数据
    def getIdxDaily(self,conf):
        if not conf.get('type') or conf['type'] != 'idx':
            raise Exception('GTADB getFFutMin conf type err')
        return self.__IDX_MKT_QUOTATION__(conf)
    # 期货日线数据
    def getFutDaily(self,conf):
        if conf['type'] == 'fut':
            return self.__FUT_QUOTATIONHISTORY__(conf)
        elif conf['type'] == 'ffut':
            return self.__FFUT_QUOTATION__(conf)
        else:
            raise Exception('GTADB getFutDaily type undefine:%s'%(conf['type']))
    def getFFutDaily(self,conf):
        return self.getFutDaily(conf)

    def __format_min__(self,data):
        for i in range(len(data)):
            date = data[i][0]
            if type(date) == datetime:
                return data
            time = data[i][1]
            data[i] = [datetime(int(date[:4]),int(date[4:6]),int(date[6:]),int(time[:2]),int(time[2:]))] + list(data[i])[2:]
        return data

    def __min__(self,conf):
        if conf.get('preDBName'):
            rt = []
            tmp = conf['start']
            while mym(tmp) <= mym(conf['end']):
                conf['tableName'] = self.__sql.buildTableName(conf, tmp)
                rt += self.dbRunSql("%s%s"%(conf['preDBName'],mym(tmp)),self.__sql.build(conf))
                if tmp.month != 12:
                    tmp = datetime(tmp.year,tmp.month+1,1)
                else:
                    tmp = datetime(tmp.year+1,1,1)
            return self.__format_min__(rt)
        else:
            raise Exception('GTADB __stock_min__ conf err:%s'%(str(conf)))

    def getStockIdxMinDBName(self, tail=''):
        return 'GTA_SEL1_TRDMIN_%s'%(tail)
    def getStockIdxMinTableName(self, market, period=None, tail=None):
        if not period :
            return '%sL1_TRDMIN'%(market)
        if not tail:
            return '%sL1_TRDMIN%s_'%(market, period)
        return '%sL1_TRDMIN%s_%s'%(market, period, tail)
    # 股票、指数分钟级数据(数据跨度一个月，以start为准)
    def getStockIdxMin(self,conf):
        if not conf.get('type') or conf['type'] not in ['stk','idx']:
            raise Exception('GTADB getFFutMin conf type err')
        if not conf.get('groupMarket') or conf['groupMarket'] not in ['SH','SZ']:
            raise Exception('GTADB __stock_min__ conf groupMarket undefined:%s'%(conf.get('groupMarket')))
        conf['preDBName'] = self.getStockIdxMinDBName()
        conf['dateName'] = ['TDATE','MINTIME']
        conf['preTableName'] = self.getStockIdxMinTableName(conf['groupMarket'])
        conf['codeName'] = 'SECCODE'
        
        return self.__min__(conf)
    def getFFutMinDBName(self, tail=''):
        return 'GTA_FFL2_TRDMIN_%s'%(tail)
    def getFFutMinTableName(self, period=None, tail=None):
        if not period:
            return 'FFL2_TRDMIN'
        if not tail:
            return 'FFL2_TRDMIN%s_'%(period)
        return 'FFL2_TRDMIN%s_%s'%(period, tail)
    # 股指期货分钟级数据
    def getFFutMin(self,conf):
        if not conf.get('type') or conf['type'] != 'ffut':
            raise Exception('GTADB getFFutMin conf type err')
        conf['preDBName'] = self.getFFutMinDBName()
        conf['dateName'] = ['TDATE','TTIME']
        conf['preTableName'] = self.getFFutMinTableName()
        conf['codeName'] = 'IFCD'
        #self.__sql.addOtherWhere(conf,"MINTQ <> '0'")
        return self.__min__(conf)
    # 商品期货分钟级数据
    def getFutMinDBName(self, tail=''):
        return 'GTA_MFL1_TRDMIN_%s'%(tail)
    def getFutMinTableName(self, period=None, tail=None):
        if not period:
            return 'MFL1_TRDMIN'
        if not tail:
            return 'MFL1_TRDMIN%s_'%(period)
        return 'MFL1_TRDMIN%s_%s'%(period, tail)
    def getFutMin(self,conf):
        if not conf.get('type') or conf['type'] != 'fut' :
            raise Exception('GTADB getFutMin conf type err')
        conf['preDBName'] = self.getFutMinDBName()
        conf['codeName'] = 'CONTRACTID'
        conf['preTableName'] = self.getFutMinTableName()
        conf['dateName'] = 'TDATETIME'
        self.__sql.addOtherWhere(conf,"MINQTY <> '0'")
        #期货分钟级数据从 2010-01-01 开始
        if conf['start'] < datetime(2010, 01, 01):
            conf['start'] = datetime(2010, 01, 01)
        #self._fusFilterZeroVolume(conf)
        return self.__min__(conf)
    def getTradeDate(self,conf):
        return self.__STK_CALENDARD__(conf)
    def getDivident(self,conf):
        return self.__STK_MKT_DIVIDENT__(conf)
    def getDomInfo(self,conf):
        return self.__PUB_MAINCONTRACT__(conf)
    #兼容
    def close(self):
        self.stop()
#test 
def printRow(data):
    for line in data:
        print line
def testAll():
    cdb = GTADB()
    cdb.start()
    conf = {}
    conf['code'] = ['000001','000002']
    conf['start'] = datetime(2014,04,01,00,00,00)
    conf['end'] = datetime(2014,05,10,00,00,00)
    conf['period'] = '60'

    conf['fields'] = 'OPENPRICE,HIGHPRICE,LOWPRICE,CLOSEPRICE'
    conf['adj'] = 'f'
    conf['groupMarket'] = 'SH'
    conf['type'] = 'stk'
    res = cdb.getStockDaily(conf)
    print 'stockDaily',len(res)

    conf['type'] = 'idx'
    res = cdb.getIdxDaily(conf)
    print 'idxDaily',len(res)

    conf['type'] = 'stk'
    conf['fields'] = 'STARTPRC,HIGHPRC,LOWPRC,ENDPRC'
    res = cdb.getStockIdxMin(conf)
    print 'stockMin',len(res)

    conf['fildes'] = 'OPNPRC,HIPRC,LOPRC,CLSPRC'
    conf['code'] = ['IF1404','IF1405']
    conf['type'] = 'ffut'
    conf['orderBy'] = 'date'
    res = cdb.getFFutMin(conf)
    print 'ffutMin',len(res)

    conf['fildes'] = 'OPENPX,HIGHPX,LOWPX,LASTPX'
    conf['type'] = 'fut'
    conf['code'] = ['A1404','A1405']
    res = cdb.getFutMin(conf)
    print 'futMin',len(res)

    #printRow(res)

def test():
    cdb = GTADB()
    cdb.start()
    conf = {}
    conf['code'] = ['A%','B%']
    conf['start'] = datetime(2005,01,01,00,00,00)
    conf['end'] = datetime(2005,12,01,00,00,00)

    res = cdb.getDomInfo(conf)
    print len(res)

if __name__ == '__main__':
    #testAll()
    test()