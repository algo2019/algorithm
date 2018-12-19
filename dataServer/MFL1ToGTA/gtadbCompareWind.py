import aly
from External.GTADBOperator import GTADBOperator
from dataServer import d
from dataServer import w


class dataMgr:
    def __init__(self):
        self.minuteList = ["01", "05", "10", "15", "30", "60"]
        self.__operator = GTADBOperator()
        self.__rc = aly.codeRecognizer()
        self._intInfo()
        self.__marketDict = {
            'DLFX': 'DCE' ,
            'ZZFX': 'CEF',
            'SHFX': 'SHF',
        }

    def _intInfo(self):
        self.__info = [0 ,0 , 0, 0, 0 ,0, 0]
        self.__count = 0

    def marketToWind(self, market):
        return self.__marketDict[market]

    def compareDB(self, start, end, minute):
        dataBase = "GTA_MFL1_TRDMIN_%s" % (start.split()[0][:-2])
        table = "MFL1_TRDMIN%s_%s" % (minute, start.split()[0][:-2])
        #instruments =['%s.%s'%(i[0],self.marketToWind(i[1])) for i in  d.wmm({
        #    'dataName':'sql',
        #    'dataBaseName':dataBase ,
        #    'sql':'select CONTRACTID,MARKET from %s group by CONTRACTID,MARKET'%(table) ,
        #}) ]
        instruments = ['A1609.DCE']

        for instrument in instruments:
            print dataBase, table, minute,instrument
            try:
                res1 = d.wsi(instrument,"open,high,low,close,volume,amt,oi","%s" % (start),"%s" % (end),"BarSize=%s" % (minute))
                print 'gta get ok'
                res = w.wsi(instrument,"open,high,low,close,volume,amt,oi","%s" % (start),"%s" % (end),"BarSize=%s" % (minute))
                print 'wind get ok'
            except Exception,e:
                print 'err: w.wsi("%s","open,high,low,close,volume,amt,oi","%s","%s","BarSize=%s")' % (instrument,start, end, minute)
                print str(e)
                continue
            res1.Times = [ str(i)[:19] for i in res1.Times]
            res.Times = [ str(i)[:19] for i in res.Times]

            for i in range(len(res1.Times)):
                dateTime = res1.Times[i]
                if dateTime not in res.Times:
                    #print dateTime,'is not in wind!'
                    #print 'err: w.wsi("%s","open,high,low,close,volume,amt,oi","%s","%s","BarSize=%s")' % (instrument,start, end, minute)
                    #print res.Times
                    #print  res.Data
                    continue
                wi = res.Times.index(dateTime)
                if minute == '01' :
                    if  wi > 0:
                        wi -= 1
                    else:
                        continue
                self.__count += 1
                for infoIndex in range(7):
                    if str(res.Data[infoIndex][wi]) == 'nan':
                        continue
                    self.__info[infoIndex] += abs((res.Data[infoIndex][wi] - res1.Data[infoIndex][i]))/res1.Data[infoIndex][i]
            self.outInfo()
    def outInfo(self):
        if self.__count != 0:
            avg = [i/(self.__count+0.0)*100 for i in self.__info]
        else:
            avg = [0 ,0 ,0 ,0 ,0 ,0 ,0]
        print 'count:%d open:%4.4f high:%4.4f low:%4.4f close:%4.4f volume:%4.4f amt:%4.4f oi:%4.4f'%(
            self.__count,avg[0],avg[1],avg[2],avg[3],avg[4],avg[5],avg[6])
        self._intInfo()

    def start(self, dateLists):
        self._intInfo()
        self.__operator.start()
        for start, end in dateLists:
            for minute in self.minuteList:
                self.compareDB(start, end, minute)
        self.__operator.stop()

w.start()
d.start()
t = dataMgr()
timeLists = [
    ["20160526 17:00:00", "20160527 17:00:00"],
]

t.start(timeLists)
w.stop()
d.stop()