# -*- coding:utf-8 -*-
import datetime

from dataBaseAPI import confMaker
import aly

class Maker(confMaker.dateConfMaker):
  def __init__(self,conf={}):
    confMaker.dateConfMaker.__init__(self,conf)
    self.set('dataName','domInfo')
    self.set('orderBy','code,date')
    if conf.get('commodity'):
      self.setCommodity(conf['commodity'])
    self.setEnd(self.getEnd() + datetime.timedelta(seconds=1))

  def setCommodity(self, commodity):
    self.set('commodity',aly.getStr(commodity))
    self.setCode()
  def getCommodity(self):
    return self.get('commodity')

  def setBeforDay(self,beforday):
    self.set('beforday',beforday)
  def getBeforDay(self):
    return self.get('beforday')

  def setAfterDay(self,afterday):
    self.set('afterday',afterday)
  def getAfterDay(self):
    return self.get('afterday')

  def setCode(self):
    self.set('code',aly.getList(self.getCommodity()))

  def getCode(self):
    if not self.get('code'):
      self.setCode()
    return self.get('code')

  def getDefaultConfTable(self):
    return Maker.DEFAULT_CONF_TABLE

  DEFAULT_CONF_TABLE = {
    'start':'1990-01-01' ,
    'end':aly.dateFormat(None) ,
    'afterday': 0 ,
    'beforday': 0 ,
    #TODO 所有品种
    'commodity':'a,b,' ,
    'code':None ,
  }
      


    