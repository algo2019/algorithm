# -*- coding:utf-8 -*-
import BaseAction
from dataBaseAPI.confMaker.sqlQueryConf import Maker

class sqlQuery(BaseAction.base):

  def action(self,conf):
    maker = Maker(conf)
    return self.getDBA().getDataBase(maker.getDataBase()).dbRunSql(maker.getDataBaseName(),maker.getSql())