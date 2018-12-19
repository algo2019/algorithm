# -*- coding:utf-8 -*-
from dataBaseAdapter import dataBase1
from dataBaseAPI import confMaker
#test
def printRow(data):
  for line in data:
    print line

def testData(db1):
  conf = {
    'dataName':'data' ,
    'start':'20140401' ,
    'end':'20140510' ,
    'code':['000001.SZ','000001.SH'] ,
    'fields':'open' ,
    'adj':'0' ,
    'period':'1d',
  }
  db1 = dataBase1()
  db1.start()
  res = db1.getData(conf)
  print 'stk idx daily',len(res)

  conf = {
    'dataName':'data' ,
    'start':'20140401' ,
    'end':'20140510' ,
    'code':['000001.SZ','000001.SH'] ,
    'fields':'open' ,
    'adj':'0' ,
    'period':'60m',
  }
  res = db1.getData(conf)
  print 'stk idx min',len(res)

  conf = {
    'dataName':'data' ,
    'start':'20140401' ,
    'end':'20140510' ,
    'code':['A1406','A1405'] ,
    'fields':'open' ,
    'adj':'0' ,
    'period':'60m',
  }
  res = db1.getData(conf)
  print 'fut min',len(res)

  conf = {
    'dataName':'data' ,
    'start':'20140401' ,
    'end':'20140510' ,
    'code':['A1406','A1405'] ,
    'fields':'open' ,
    'adj':'0' ,
    'period':'1d',
  }
  res = db1.getData(conf)
  print 'fut daily',len(res)

  conf = {
    'dataName':'data' ,
    'start':'20140401' ,
    'end':'20140510' ,
    'code':['IF1404','IF1406'] ,
    'fields':'open' ,
    'adj':'0' ,
    'period':'1d',
  }
  res = db1.getData(conf)
  print 'ffut daily',len(res)

  conf = {
    'dataName':'data' ,
    'start':'20140401' ,
    'end':'20140510' ,
    'code':['IF1404','IF1406'] ,
    'fields':'open' ,
    'adj':'0' ,
    'period':'60m',
  }
  res = db1.getData(conf)
  print 'ffut min',len(res)

  conf['code'] = ['000001.SZ','000001.SH','IF1404','IF1406','A1406','A1405']
  res = db1.getData(conf)
  print '混合 min',len(res)

  conf['code'] = ['000001.SZ','000001.SH','IF1404','IF1406','A1406','A1405']
  conf['period'] = '1d'
  res = db1.getData(conf)
  print '混合 day',len(res)

  res = db1.getDayData('000001.SZ,000001.SH,IF1404,IF1406,A1406,A1405',
    '20140401',
    '20140510',
    'close,open',
    '0')
  print '混合 getDayData',len(res)
  res = db1.getMinData('000001.SZ,000001.SH,IF1404,IF1406,A1406,A1405',
    '20140401',
    '20140510',
    '60',
    'close,open')
  print '混合 getMinData',len(res)

  res = db1.getTradeDate('20140101',None)
  print 'getTradeDate',len(res)

def testSqlQuery(db):
  conf = {
    'sql':"select TRADINGDATE,SYMBOL,OPENPRICE,HIGHPRICE,LOWPRICE,CLOSEPRICE,VOLUME from STK_MKT_QUOTATION  where  TRADINGDATE>='2001-01-02 00:00:00'  and  TRADINGDATE<'2001-04-17 00:00:00'  and ( (SYMBOL in ('000001')) ) and FILLING='0'" ,
    'dataName':'sql' ,
  }
  print 'sql',len(db.getData(conf))

def testFuts(db1):
  import datetime
  conf = {
    'dataName':'futs' ,
    'futs':[
      [u'AL1502', 60 ,datetime.datetime(2014, 10, 24, 0, 0), datetime.datetime(2014, 12, 15, 0, 0)] ,
      [u'AL1503', 60 ,datetime.datetime(2014, 11, 3, 0, 0), datetime.datetime(2014, 12, 23, 0, 0)] ,
      [u'B1405', 60 ,datetime.datetime(2014, 12, 22, 0, 0), datetime.datetime(2014, 4, 14, 0, 0)] ,
      [u'B1407', 60 ,datetime.datetime(2014, 3, 3, 0, 0), datetime.datetime(2014, 4, 29, 0, 0)] ,
      [u'B1409', 60 ,datetime.datetime(2014, 3, 18, 0, 0), datetime.datetime(2014, 5, 11, 0, 0)] ,
      [u'B1411', 60 ,datetime.datetime(2014, 9, 2, 0, 0), datetime.datetime(2014, 10, 31, 0, 0)] ,
      [u'B1501', 60 ,datetime.datetime(2014, 8, 12, 0, 0), datetime.datetime(2014, 10, 21, 0, 0)] ,
    ],
    'fields':'close,open' ,
  }
  res = db1.getData(conf)
  print 'futs min',len(res)

  maker = confMaker.futsConf.Maker()
  maker.setFuts([
      [u'AL1502', 60*60*24 ,datetime.datetime(2014, 10, 24, 0, 0), datetime.datetime(2014, 12, 15, 0, 0)] ,
      [u'AL1503', 60*60*24 ,datetime.datetime(2014, 11, 3, 0, 0), datetime.datetime(2014, 12, 23, 0, 0)] ,
     ])
  '''
  conf = {
    'dataName':'futs' ,
    'futs':[
      [u'AL1502', 60*60*24 ,datetime.datetime(2014, 10, 24, 0, 0), datetime.datetime(2014, 12, 15, 0, 0)] ,
      [u'AL1503', 60*60*24 ,datetime.datetime(2014, 11, 3, 0, 0), datetime.datetime(2014, 12, 23, 0, 0)] ,
     ],
    'fields':'close,open' ,
  }
  '''
  res = db1.getData(maker.get())
  printRow(res)
  print 'futs daily',len(res)

def testDomInfo(db1):  
  maker = confMaker.domInfoConf.Maker()
  maker.setDateRange('20010101','20101212')
  maker.setAfterDay(10)
  maker.setBeforDay(20)
  maker.setCommodity('al,ag,a,b,i')
  '''
  conf = {
          'dataName':'domInfo' ,
          'start':'20050101' ,
          'end':'20051212' ,
          'afterday':10 ,
          'beforday':20 ,
          'commodity':['a','B'] ,
        }
        
  '''
  res = db1.getData(maker.get())
  printRow(res)
  print 'domInfo',len(res)

def testDivident(db1):
  res = db1.getData({'code':'000001.SZ,000001.SH','dataName':'divident'})
  print 'getDivident',len(res)

def test(db1):
  conf = {
    'dataName':'data' ,
    'start':'20160201' ,
    'end':'20160222' ,
    'code':['MA1609'] ,
    'fields':'open,high,low,close,volume' ,
    'adj':'0' ,
    'period':'60m',
  }
  res = db1.getData(conf)
  for line in res:
    print str(line[0]),str(line[1:])

if __name__ == '__main__':
  db = dataBase1()
  db.start()
  #testData(db)
  #testDivident(db)
  #testDomInfo(db)
  #testFuts(db)
  #testSqlQuery(db)
  test(db)
  db.close()
