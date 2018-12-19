# -*- coding:utf-8 -*-
from pyalgotrade.barfeed import membf
from pyalgotrade import dataseries
from pyalgotrade import bar
from pyalgotrade import utils
import dataCache
import dataServer
class DataseriesParams(object):
    Fields = ['open', 'high', 'low', 'close', 'volume' ]
    Periods = ['1d','1m','5m','10m','15m','30m','60m']

class BarFeed(membf.BarFeed):
    def __init__(self, instruments,start,end,period='1d',useAdj='0',maxLen=dataseries.DEFAULT_MAX_LEN,maxSize=dataCache.MAXSIZE):
        self.__d = dataServer.dataServer()
        self.__instruments = instruments
        self.__start = start
        self.__end = end
        self.__useAdj = useAdj
        self.__started = False
        self.__currDateTime = None
        self.__maxSize = maxSize
        bars = {}
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
        membf.BarFeed.__init__(self, self.__frequency, maxLen)
        self.addBarsFromDataServer()
        
    def barsHaveAdjClose(self):
        if self.__useAdj == '0':
            return False
        else:
            return True
    def addBarsFromDataServer(self):
        conf = {
            'dataName':'data',
            'code':self.__instruments,
            'fields':self.__fields,
            'start':self.__start,
            'end':self.__end,
            'period':self.__period,
            'adj':self.__useAdj,
        }
        self.__d.start()
        data = self.__d.wmm(conf)
        self.__d.stop()
        #if not data:
         #   raise Exception('get no data')
        bars = {}
        for line in data:
            if line and len(line) >= 7:
                if bars.get(line[1]) == None:
                    bars[line[1]] = []
                if not self.__useAdj:
                    _bar = bar.BasicBar(line[0],line[2],line[3],line[4],line[5],line[6],None,self.__frequency)
                else:
                    _bar = bar.BasicBar(line[0],line[2],line[3],line[4],line[5],line[6],line[5],self.__frequency)
                bars[line[1]].append(_bar)
        for key in bars:
            self.addBarsFromSequence(key,bars[key])
#test   
def test():
    import time
    ds = BarFeed(['600000.SH','000001.SZ'],'20150301','20150410','1m')
    t = time.time()
    bars = ds.getNextBars()
    while bars:
        b = bars['000001.SH']
        print b.getDateTime(),b.getClose()
        bars = ds.getNextBars()
        
    print 'test over'

if __name__ == '__main__':
    test()