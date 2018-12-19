# -*- coding:utf-8 -*-
import datetime

import BaseAction
import aly
from dataBaseAPI.confMaker.domInfoConf import Maker


class domInfo(BaseAction.base):
  # 获取超出指定开始结束日期加上延迟时间的交易日列表
  def __getTradingList(self):
    if self.__maker.getBeforDay() < 10:
      delayS = self.__maker.getBeforDay()*-1 - 10
    else:
      delayS = self.__maker.getBeforDay()*-2
    if self.__maker.getAfterDay() < 10:
      delayE = self.__maker.getAfterDay() + 10
    else:
      delayE = self.__maker.getAfterDay() * 2
    return self.getDBA().getTradeDate(aly.getDateFormator().format(self.__maker.getStart(),delayS),aly.getDateFormator().format(self.__maker.getEnd(),delayE))

  #设置延迟范围
  def __setDelayRange(self, _rt):
    dataList = self.__getTradingList()
    startIndex = -1
    endIndex = float("inf") 
    for line in _rt:
      if line[1] in dataList:
        startIndex = dataList.index(line[1]) - self.__maker.getBeforDay()
      if line[2] in dataList:
        endIndex = dataList.index(line[2]) + self.__maker.getAfterDay()
      if startIndex < 0:
        startIndex = 0
      if endIndex >= len(dataList):
        endIndex = len(dataList) - 1
      line[1] = dataList[startIndex]
      line[2] = dataList[endIndex]
    return _rt

  #返回数据处理,查找合约范围
  def __getDomDateRange(self, rt):
    lastCode = ''
    start = None
    _rt = []
    line = ''
    lastDate = ''
    for i in range(len(rt)):
      line = rt[i]
      if lastCode == '':
        lastCode = line[2]
        start = line[0]
      #品种改变
      if line[2] > lastCode:
        _rt.append([lastCode,start,lastDate])
        lastCode = line[2]
        start = line[0]
      lastDate = line[0]
    if line:
      _rt.append([lastCode,start,line[0]])
    return _rt

  def action(self, conf):
    self.__maker = Maker(conf)
    _rt = self.__getDomDateRange(self.getDBA().getDataBase('gta').getDomInfo(self.__maker.get()))
    rt = self.__setDelayRange(_rt)
    return rt