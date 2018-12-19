# -*- coding:utf-8 -*-
from dataBaseAPI import confMaker


class Maker(confMaker.BaseConfMaker):
    def __init__(self, conf={}):
        confMaker.BaseConfMaker.__init__(self, conf)
        self.set('dataName', 'sql')

    def setSql(self, sql):
        self.set('sql', sql)

    def getSql(self):
        return self.get('sql')

    def setDataBase(self, dbs):
        self.set('dataBase', dbs)

    def getDataBase(self):
        return self.get('dataBase')

    def setDataBaseName(self, dbName):
        self.set('dataBaseName', dbName)

    def getDataBaseName(self):
        return self.get('dataBaseName')

    def getDefaultConfTable(self):
        return Maker.DefaultConf

    def getDefaultConf(self, confName):
        if confName == 'dataBaseName':
            return Maker.DefaultConf[confName][self.getDataBase()]
        else:
            return confMaker.BaseConfMaker.getDefaultConf(self, confName)

    DefaultConf = {
        'dataBase': 'gta',
        'dataBaseName': {
            'gta': 'GTA_QIA_QDB',
            'choice': 'test',
        }
    }
