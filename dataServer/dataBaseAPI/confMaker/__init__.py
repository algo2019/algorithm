# -*- coding:utf-8 -*-
import aly
import datetime



class BaseConfMaker(object):
    def __init__(self, conf=None, defaultConfTableObj=None):
        if conf is None:
          conf = {}
        self.__conf = conf
        if defaultConfTableObj:
            self.__defaultConfTable = defaultConfTableObj
        else:
            self.__defaultConfTable = self.getDefaultConfTable()

    def setDataName(self, dataName):
        self.__conf['dataName'] = dataName

    def get(self, confName=None):
        if not confName:
            return self.__conf
        if self.__conf.get(confName) is not None:
            return self.__conf[confName]
        else:
            return self.getDefaultConf(confName)

    def has(self, confName):
        if self.__conf.get(confName) is not None:
            return True
        else:
            return False

    def set(self, confName, confValue):
        self.__conf[confName] = confValue

    def getDefaultConfTable(self):
        return {}

    def getDefaultConf(self, confName):
        if not confName:
            return self.__defaultConfTable
        if self.__defaultConfTable.get(confName) is not None:
            return self.__defaultConfTable[confName]
        else:
            raise Exception('配置没有缺省值：%s' % (confName))

    def setCode(self, code):
        self.set('code', aly.getList(code))

    def getCode(self):
        return self.get('code')


# 拥有 开始-结束 的配置对象
class dateConfMaker(BaseConfMaker):
    def __init__(self, conf={}, defaultConfTableObj=None):
        BaseConfMaker.__init__(self, conf, defaultConfTableObj)
        self.setDateRange(self.getStart(), self.getEnd())
        self.set('orderBy', 'date')

    def setDateRange(self, start, end):
        self.setStart(start)
        self.setEnd(end)

    def setStart(self, start):
        w = self.get()['client']
        start = aly.dateFormat(start)
        if self.get('tradingday'):
            start = datetime.datetime.combine(w.tdaysoffset(1, start).Data[0][0].date(), datetime.time(20, 59, 59))
        self.set('start', start)

    def getStart(self):
        return self.get('start')

    def getDefaultConf(self, dataName):
        if dataName == 'tradingday':
            return self.get().get(dataName, False)
        if dataName == 'includeend':
            return self.get().get(dataName, False)
        if dataName in ['start', 'end']:
            return self.get().get(dataName)
        else:
            return BaseConfMaker.getDefaultConf(self, dataName)

    def setEnd(self, end):
        w = self.get()['client']
        if self.get('includeend'):
            end = datetime.datetime.combine(w.tdaysoffset(0, end).Data[0][0].date(), datetime.time(15, 0, 1))
        elif self.get('tradingday'):
            end = datetime.datetime.combine(w.tdaysoffset(1, end).Data[0][0].date(), datetime.time(15, 0, 1))
        else:
            end = aly.dateFormat(end)
        self.set('end', end)

    def getEnd(self):
        return self.get('end')