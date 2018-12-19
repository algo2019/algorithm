# -*- coding:utf-8 -*-
from pyalgotrade import barfeed
from pyalgotrade import dataseries
from pyalgotrade import bar
from pyalgotrade import utils
import dataCache
from dataServer import d
class DataseriesParams(object):
    Fields = ['open', 'high', 'low', 'close', 'volume' ]
    Periods = ['1d','1m','5m','10m','15m','30m','60m']

class BarFeed(barfeed.BaseBarFeed):
    def __init__(self, instruments,start,end,period='1d',useAdj='0',maxLen=dataseries.DEFAULT_MAX_LEN,maxSize=dataCache.MAXSIZE):
        self.__instruments = instruments
        self.__start = start
        self.__end = end
        self.__useAdj = useAdj
        self.__started = False
        self.__currDateTime = None
        self.__maxSize = maxSize
        self.__bars = {}
        self.__nextPos = {}
        #fields
        self.__fields = DataseriesParams.Fields
        #周期判断
        if period == '1d':
            self.__period = period
            self.__frequency = bar.Frequency.DAY
        else:
            if period in DataseriesParams.Periods:
                self.__period = period
                self.__frequency = bar.Frequency.DAY
            else:
                raise Exception('%s period not support'%(period))
            if self.__useAdj != '0':
                raise Exception('Frequency.MINUTE not support Adj') 
        #
        barfeed.BaseBarFeed.__init__(self, self.__frequency, maxLen)
        for instrument in self.__instruments:
            self.registerInstrument(instrument)      
        #时间序列
        self.setDataCache()
    
    def getCurrentDateTime(self):
        return self.__currDateTime

    def start(self):
        self.startDataCache()
        self.__started = True

    def stop(self):
        pass

    def join(self):
        pass
    def getDataCache(self):
        return self.__dataCache
    def setDataCache(self,_dataCache=dataCache.dataCache):
        self.__dataCache = _dataCache(self.getTimes(),self.__instruments,self.__fields,self.__period,self.__useAdj,maxSize=self.__maxSize)        
    def startDataCache(self,_dataCache=dataCache.dataCache):
        self.__dataCache.start()
        self.updateBars()
        
    def reset(self):
        barfeed.BaseBarFeed.reset(self)
        self.initDataCache()

    #设置时间序列
    def getTimes(self):
        dayTimes = None
        #数据库中读取交易日序列
        d.start()
        res = d.tdays(self.__start,self.__end)
        d.stop()
        if res.ErrorCode == 0:
            dayTimes = res.Data[0]
        else:
            dayTimes = self.getDayTimes()
        return dayTimes

    def getDayTimes(self,dayTimes):
        raise NotImplementedError()
   
    def eof(self):
        ret = True
        # Check if there is at least one more bar to return.
        for instrument, bars in self.__bars.iteritems():
            nextPos = self.__nextPos[instrument]
            if nextPos < len(bars) or self.updateBars():
                ret = False
                break
        return ret
    def barsHaveAdjClose(self):
        if self.__useAdj == '0':
            return False
        else:
            return True
    def peekDateTime(self):
        ret = None
        for instrument, bars in self.__bars.iteritems():
            nextPos = self.__nextPos[instrument]
            if nextPos < len(bars):
                ret = utils.safe_min(ret, bars[nextPos].getDateTime())
        if ret == None and self.updateBars():
            return self.peekDateTime()
        return ret
    def getNextBars(self):
        # All bars must have the same datetime. We will return all the ones with the smallest datetime.
        smallestDateTime = self.peekDateTime()
        if smallestDateTime is None:
            return None

        # Make a second pass to get all the bars that had the smallest datetime.
        ret = {}
        for instrument, bars in self.__bars.iteritems():
            nextPos = self.__nextPos[instrument]
            if nextPos < len(bars) and bars[nextPos].getDateTime() == smallestDateTime:
                ret[instrument] = bars[nextPos]
                self.__nextPos[instrument] += 1

        if self.__currDateTime == smallestDateTime:
            raise Exception("Duplicate bars found for %s on %s" % (ret.keys(), smallestDateTime))

        self.__currDateTime = smallestDateTime
        return bar.Bars(ret)
    #更新bars
    def updateBars(self):
        dataList = self.__dataCache.getData()
        if not dataList :
            return 0

        self.__bars = {}
        self.__nextPos = {}
        for line in dataList:
            if line and len(line) >= 7:
                if self.__bars.get(line[1]) == None:
                    self.__bars[line[1]] = []
                    self.__nextPos[line[1]] = 0
                if not self.__useAdj:
                    _bar = bar.BasicBar(line[0],line[2],line[3],line[4],line[5],line[6],None,self.__frequency)
                else:
                    _bar = bar.BasicBar(line[0],line[2],line[3],line[4],line[5],line[6],line[5],self.__frequency)
                self.__bars[line[1]].append(_bar)
        return 1
    def loadAll(self):
        for dateTime, bars in self:
            pass
#test
def test():
    import time
    ds = BarFeed(['600000.SH','000001.SZ'],'20150301','20150410','1m')
    t = time.time()
    ds.start()
    bars = ds.getNextBars()
    c = 1
    while bars:
        if time.time() - t > 0.5:
            print 'signal',c
        t = time.time()
        c += 1
        b = bars['000001.SZ']
        bars = ds.getNextBars()
        
    print 'signal',c
    print 'test over'

if __name__ == '__main__':
    test()