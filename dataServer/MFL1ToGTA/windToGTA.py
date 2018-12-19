import time

import aly
from External.GTADBOperator import GTADBOperator
from dataServer import d
from dataServer import w


class dataMgr:
    def __init__(self):
        self.minuteList = [ '01', '05', '10', '15', "30", "60"]
        self.__operator = GTADBOperator()
        self.__rc = aly.codeRecognizer()
    def __del__(self):
        w.stop()
    def hasNan(self, res, i):
        try:
            for index in range(7):
                if str(res.Data[index][i]) == 'nan':
                    return True
        except Exception, e:
            print res.Data
            return True
        return False

    def InsertByOne(self, res, dbName, table, instrument):
        for i in range(len(res.Times)):
            if self.hasNan(res, i):
                continue
            TDATETIME = res.Times[i]
            CONTRACTID, MARKET = instrument.split('.')
            OPENPX = res.Data[0][i]
            HIGHPX = res.Data[1][i]
            LOWPX = res.Data[2][i]
            LASTPX = res.Data[3][i]
            MINQTY = res.Data[4][i]
            TURNOVER = res.Data[5][i]
            OPENINTS = res.Data[6][i]
            CHGMIN = LASTPX - OPENPX
            CHGPCTMIN = '%4.4f' % (CHGMIN / OPENPX)
            VARIETIES = '--'
            MFLXID = '--'
            UNIX = int(time.mktime(time.strptime(res.Times[i], "%Y-%m-%d %H:%M:%S")))
            self.__operator.insertValue (dbName, table, map(str, (
                CONTRACTID, TDATETIME, OPENPX, HIGHPX, LOWPX, LASTPX, MINQTY, TURNOVER, OPENINTS, CHGMIN, CHGPCTMIN,
                VARIETIES, MFLXID, MARKET, UNIX)))

    def getInsertList(self, res, instrument):
        insertList = []
        for i in range(len(res.Times)):
            if self.hasNan(res, i):
                continue
            TDATETIME = res.Times[i]
            CONTRACTID, MARKET = instrument.split('.')
            OPENPX = res.Data[0][i]
            HIGHPX = res.Data[1][i]
            LOWPX = res.Data[2][i]
            LASTPX = res.Data[3][i]
            MINQTY = res.Data[4][i]
            TURNOVER = res.Data[5][i]
            OPENINTS = res.Data[6][i]
            CHGMIN = LASTPX - OPENPX
            CHGPCTMIN = CHGMIN / OPENPX
            VARIETIES = '--'
            MFLXID = '--'
            UNIX = int(time.mktime(time.strptime(res.Times[i], "%Y-%m-%d %H:%M:%S")))
            listStr =  "'%s','%s','%f','%f','%f','%f','%d','%f','%d','%f','%f','%s','%s','%s','%d'"%(
                CONTRACTID, TDATETIME,OPENPX, HIGHPX, LOWPX, LASTPX, MINQTY, TURNOVER,OPENINTS, CHGMIN, CHGPCTMIN, VARIETIES, MFLXID, MARKET,UNIX
            )
            insertList.append(listStr)
        return insertList



    def updateDB(self, start, end, instruments, minute):
        dataBase = "GTA_MFL1_TRDMIN_%s" % (start[:-2])
        table = "MFL1_TRDMIN%s_%s" % (minute, start[:-2])
        for instrument in instruments:
            print dataBase, table, minute,instrument
            #res1 = d.wsi(instrument,"open,high,low,close,volume,amt,oi","%s 00:00:00" % (start),"%s 23:59:59" % (end),"BarSize=%s" % (minute))
            #print 'gta get ok'
            res = w.wsi(instrument,"open,high,low,close,volume,amt,oi","%s 00:00:00" % (start),"%s 23:59:59" % (end),"BarSize=%s" % (minute))
            print 'wind get ok'
            res.Times = [str(i)[:19] for i in res.Times]
            #res1.Times = [str(i)[:19] for i in res1.Times]
            self.__operator.insertValues(dataBase, table, self.getInsertList(res,instrument))
            #self.InsertByOne(res, dataBase, table, instrument)

    def start(self, dateLists, instrument=None):
        self.__operator.start()
        #marketCodes = ['a599010401000000' , 'a599010201000000', 'a599010301000000']
        marketCodes = ['a599010401000000']
        if instrument:
            add = False
        else:
            add = True
        for start, end in dateLists:
            instruments = []
            for marketCode in marketCodes:
                for i in w.wset("sectorconstituent", "date=%s;sectorid=%s" % (start, marketCode)).Data[1]:
                    if not add :
                        if i == instrument:
                            add = True
                        else:
                            continue
                    if self.__rc.recogniseType(i) == 'fut':
                        instruments.append(i)
            for minute in self.minuteList:
                self.updateDB(start, end, instruments, minute)

        self.__operator.stop()

w.start()
d.start()
t = dataMgr()
timeLists = [
    ["20160301", "20160331"] ,
    ["20160401", "20160430"] ,
    ["20160501", "20160531"] ,
]

t.start(timeLists)
w.stop()
d.stop()