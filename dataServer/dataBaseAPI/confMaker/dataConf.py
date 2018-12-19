# -*- coding:utf-8 -*-
from dataBaseAPI import confMaker
import aly
import datetime
class Maker(confMaker.dateConfMaker):
  def __init__(self,conf=None):
    confMaker.dateConfMaker.__init__(self,conf)
    self.set('dataName','data')
    self.__cr = aly.getCodeRecognizer(aly.getList(self.getCode()))
    self.setPeriod(self.getPeriod())
    self.setCode(self.getCode())
    self.setFields(self.getFields())
  def setCode(self, code):
    self.set('code', self.getCodeRecognizer().getCodeList())
  def getNoFixCode(self):
    return [i.split('.')[0] for i in self.getCode()]
  def get(self,confName=None):
    if not confName:
      if self.has('code'):
        self.set('code', self.getNoFixCode())
    return confMaker.dateConfMaker.get(self, confName)
  def setFields(self,fields):
    '''
    for field in aly.getList(fields):
      if not self.isOk('fields',field):
        raise Exception('字段未定义：%s'%(field))
    '''
    self.set('fields',aly.getStr(fields))
  def getFields(self):
    return self.get('fields')

  def setAdj(self,adj):
    if not self.isOk('adj',adj):
      raise Exception('复权标识未定义：%s'%(adj))
    self.set('adj',adj)
  def getAdj(self):
    return self.get('adj')

  def setMarket(self,market):
    self.set('market',market)
  def getMarket(self):
    return self.get('market')

  def setMarketCode(self,marketCode):
    self.set('marketCode',marketCode)
  def getMarketCode(self,typeStr=None):
    if typeStr is None :
      if not self.get('marketCode'):
        self.setMarketCode(self.getCodeRecognizer().getMarketCode())
      return self.get('marketCode')
    else:
      return self.get('marketCode')[typeStr]

  def setType(self,typeStr):
    self.set('type',typeStr)
  def getType(self):
    return self.get('type')

  def getCodeRecognizer(self):
    return self.__cr
  def rtBackTest(self, rt):
    if len(rt) == 0:
      return rt
    mergeIndex = []
    backInstrument = self.getCodeRecognizer().unRecognise('%s.%s'%(rt[0][1],self.getMarket()[self.getCode().index(rt[0][1])]))
    for index in range(len(rt)):
        #0 dateTime 1 instrument 2 open 3 high 4 low 5 close 6 volume
        line = rt[index]
        if line[0].time() == datetime.time(21, 0, 0) or line[0].time() == datetime.time(9, 0, 0):
            mergeIndex.append(index)
            rt[index+1][2] = line[2]
            if rt[index+1][3] < line[2]:
              rt[index + 1][3] = line[2]
            if rt[index+1][4] > line[2]:
              rt[index + 1][4] = line[2]
            rt[index+1][6] += line[6]
        else:
            line[1] = backInstrument

    for index in range(1, len(mergeIndex)+1):
      del rt[mergeIndex[0 - index]]
    return rt

  def rtCodeRecognize(self,rt):
    for line in rt:
      line[1] = self.getCodeRecognizer().unRecognise('%s.%s'%(line[1],self.getMarket()[self.getCode().index(line[1])]))
    return list(rt)
  def setGroupMarket(self,market):
    self.set('groupMarket',market)
  def getGroupMarket(self):
    return self.get('groupMarket')

  def isOk(self,field,value):
    return value in self.getFieldRange(field)

  def getDefaultConfTable(self):
    return Maker.DEFAULT_CONF_TABLE

  def getFieldRange(self,field):
    return Maker.FIELD_RANGE_TABLE[field.lower()]
  
  def setPeriod(self,period):
    if not self.isOk('period',period):
      raise Exception('周期未定义：%s'%(period))
    if period == '1h':
      period = '60m'
    if period == '1d':
      self.set('period',period)
    elif period[-1:] == 'm':
      self.set('period','%.2d'%(int(period[:-1])))
    else:
      self.set('period',period)
  def getPeriod(self):
    return self.get('period')

  FIELD_RANGE_TABLE = {
    'period':['1d','1m','5m','10m','15m','30m','60m','1h','01','05','10','15','30','60'] ,
    'adj':['0','f','b']
  }
  DEFAULT_CONF_TABLE = {
    'fields':'open,high,low,close,volume' ,
    'period':'1d' ,
    'adj':'0' ,
    'start':'1990-01-01' ,
    'marketCode':0 ,
    'market':None ,
    'end':aly.dateFormat(None) ,
  }