# -*- coding:utf-8 -*-
import BaseAction
import aly
from dataBaseAPI.confMaker.futsConf import Maker

# 获取几个合约的数据指定时间段
class futs(BaseAction.base):
  def __set_daily__(self,maker):
    maker.setCode([])
    for line in maker.getFuts() :
      maker.addCode(line[0])

  def __set_min__(self,maker):
    for line in maker.getFuts():
      if not maker.getCode() :
        maker.setStart(line[2])
        maker.setEnd(line[3])
        maker.setCode([])
      maker.addCode(line[0])
      if maker.getStart() > aly.dateFormat(line[2]) :
        maker.setStart(line[2])
      if maker.getEnd() < aly.dateFormat(line[3]) :
        maker.setEnd(line[3])

  def action(self,conf):
    maker = Maker(conf)
    if maker.getPeriod() == '1d':
      self.__set_daily__(maker)
    else:
      self.__set_min__(maker)
    maker.setDataName('data')
    return self.getDBA().getData(maker.get())
  
  