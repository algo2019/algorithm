#-*- coding:utf-8 -*-
from pyalgotrade.resamplebase import *
import datetime

TRADING_DATE = []

def addToTradingDate(dateTime):
    if len(TRADING_DATE) == 0 or dateTime.date() != TRADING_DATE[-1]:
        TRADING_DATE.append(datetime.datetime(dateTime.year, dateTime.month, dateTime.day))
    '''
    #dataTime 不按顺序添加
    if dateTime.date() not in TRADING_DATE:
        TRADING_DATE.append(dateTime.date())
        #TRADING_DATE.sort()
    '''

def getLastTradingDate(dateTime):
    if dateTime not in TRADING_DATE:
        raise Exception('%s is not in TRADING_DATE list'%(str(dateTime)))
    index = TRADING_DATE.index(dateTime)
    if index:
        return TRADING_DATE[index-1]
    else:
        return dateTime + datetime.timedelta(days=-1)

class DayRange(TimeRange):
    def __init__(self, dateTime):
        self.__begin = datetime.datetime(dateTime.year, dateTime.month, dateTime.day)
        lastTradingDate = getLastTradingDate(self.__begin)
        self.__begin_real = datetime.datetime(lastTradingDate.year, lastTradingDate.month, lastTradingDate.day, 17, 0, 0)
        self.__end_read = datetime.datetime(self.__begin.year, self.__begin.month, self.__begin.day, 17, 0, 0)
        #if not dt.datetime_is_naive(dateTime):
        #    self.__begin = dt.localize(self.__begin, dateTime.tzinfo)
        self.__end = self.__begin + datetime.timedelta(days=1)

    def belongs(self, dateTime):
        return dateTime >= self.__begin_real and dateTime < self.__end_read

    def getBeginning(self):
        return self.__begin

    def getEnding(self):
        return self.__end
    def test(self):
        print '%s-%s %s-%s'%(self.__begin,self.__end,self.__begin_real,self.__end_read)

def test():
    from dataServer import d
    d.start()
    tdays = d.tdays('20110101','20110201').Data[0]
    d.stop()
    for i in tdays:
        addToTradingDate(i)
        DayRange(i).test()
        
if __name__ == '__main__':
    test()