# -*- coding:utf-8 -*-
import dataServer
import threading
from pyalgotrade import logger

Periods = {'1d':1,'1m':60*4,'5m':12*4,'10m':6*4,'15m':4*4,'30m':2*4,'60m':4}
MAXSIZE = 10000
BLOCKNUM = 2

class dataCache(threading.Thread):

    LOGGER_NAME = "dataCache"

    def __init__(self,times,instruments,fields,period,useAdj,blockNum=BLOCKNUM,maxSize=MAXSIZE,dsObj=None):
        #缓冲区数目
        self.__blockNum = blockNum
        #每块缓冲区时间跨度
        self.__maxSize = maxSize/(len(fields) * len(instruments) * Periods[period] )
        if not self.__maxSize:
            self.__maxSize = 1
        #时间序列
        self.__times = times
        #查询字符串
        self.__instrumentStr = ','.join(instruments)
        self.__fieldStr = ','.join(fields)
        self.__useAdj = useAdj
        #缓冲区初始化 [状态，数据编号，数据区]
        self.__block = [[0,-1,None] for i in range(self.__blockNum)]
        #用于块计数
        self.__blockCount = 0
        #
        self.__logger = logger.getLogger(dataCache.LOGGER_NAME)
        if dsObj:
            self.__d = dsObj
        else:
            self.__d = dataServer.dataServer()
        self.__period = period
        self.__conR = threading.Condition()
        self.__conG = threading.Condition()
        self.__wait = False
        threading.Thread.__init__(self) 

    def run(self):
        #检测是否有过期过缓冲区
        self.__d.start()
        self.__needCheck = False
        while 1:
            self.__needCheck = False
            for block in self.__block:
                if block[0] == 0:
                    if not self.refresh(block):
                        self.__d.stop()
                        self.__conG.acquire()
                        self.__conG.notify()
                        self.__conG.release()
                        return
                    else:
                        self.__needCheck = True
                        self.__conG.acquire()
                        self.__conG.notify()
                        self.__conG.release()
            self.__conR.acquire()
            if not self.__needCheck :
                self.__conR.wait()
            else:
                self.__conR.release()
    def getConf(self,block):
        startIndex = (self.__blockCount)*self.__maxSize
        self.__blockCount += 1
        endIndex =  self.__blockCount*self.__maxSize
        if endIndex >= len(self.__times):
            endIndex = len(self.__times) - 1
        if startIndex >= endIndex:
            return 0
        self.__logger.info("refresh _conf:%s end:%s period:%s PriceAdj:%s" % (
                self.__times[startIndex],
                self.__times[endIndex],
                self.__period,
                str(self.__useAdj)
            ))
        conf = {
            'dataName':'data',
            'code':self.__instrumentStr,
            'fields':self.__fieldStr,
            'start':self.__times[startIndex],
            'end':self.__times[endIndex],
            'period':self.__period,
            'adj':self.__useAdj,
        }
        return conf
    def refresh(self,block):
        block[1] = self.__blockCount
        conf = self.getConf(block)
        if not conf:
            return conf
        block[2] = self.__d.wmm(conf)
        block[0] = 1
        if block[2] != None:
            self.__logger.info("refresh redeay")
            return 1
        else:
            raise Exception('dataCache Error')

    def getData(self):
        self.__conG.acquire()
        rtBlock = [0,float("inf"),None]
        while not rtBlock[0]:
            for block in self.__block:
                if block[0] and block[1] < rtBlock[1]:
                    rtBlock = block
            if not rtBlock[0]:
                if self.isAlive():
                    self.__conG.wait()
                    self.__conG.release()
                    return self.getData()
                else:
                    self.__conR.acquire()
                    self.__conR.notify()
                    self.__conR.release()
                    return None
        rt = rtBlock[2]
        self.__conR.acquire()
        rtBlock[0] = 0
        self.__needCheck = True
        self.__conR.notify()
        self.__conR.release()
        self.__conG.release()
        return rt
#test
def test(): 
    from dataServer import d
    d.start()
    times = d.tdays('20141101','20141111').Data[0]
    d.stop()
    instruments = ['000001.SZ','600000.SH']
    fields = ['open', 'high', 'low', 'close', 'volume' ]
    period = '1m'

    dc = dataCache(times,instruments,fields,period,useAdj='0',maxSize=500)
    dc.start()
    data = dc.getData()
    while data:
        print len(data)
        data = dc.getData()
    print 'test over'

if __name__ == '__main__':
    test()