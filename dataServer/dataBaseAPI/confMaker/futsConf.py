# -*- coding:utf-8 -*-
from dataBaseAPI import confMaker
import aly

class Maker(confMaker.dateConfMaker):
  def __init__(self,conf={}):
    confMaker.dateConfMaker.__init__(self,conf)
    self.set('dataName','futs')
    self.set('type','fut')
    self.set('orderBy','date')

  def getFutsPeriod(self):
    return self.getFuts()[0][1]

  def getPeriod(self):
    if self.get('period'):
      return self.get('period')

    if type(self.getFutsPeriod()) == int and self.getFutsPeriod()%60 == 0:
      if self.getFutsPeriod()%(60*60*24) == 0:
        self.setPeriod('1d')
      else:
        self.setPeriod('%dm'%(self.getFutsPeriod()/60))
    elif type(self.getFutsPeriod() == str):
      self.setPeriod(self.getFutsPeriod())
    else:
      raise Exception('周期未定义：%s'%(str(self.getFutsPeriod())))
  def setPeriod(self,period):
    self.set('period',period)

  def setFuts(self, futs):
    if type(futs) == list and type(futs[0]) == list:
      self.set('futs',futs)
    else:
      raise Exception('参数应为二维数组！')
  def getFuts(self):
    return self.get('futs')

  def addCode(self, code):
    self.getCode().append(code)

  def addFut(self,fut):
    if type(fut) == list:
       self.get('futs').append(fut)
    else:
      raise Exception('参数应为一维数组！')

  def setFields(self,fields):
    self.set('fields',aly.getStr(fields))
  def getFields(self,fields):
    self.get('fields')

  def getDefaultConfTable(self):
    return Maker.DEFAULT_CONF_TABLE

  DEFAULT_CONF_TABLE = {
    'futs':[] ,
    'fields':'open,high,low,close,volume' ,
    'period':0 ,
    'code':0 ,
  }
    