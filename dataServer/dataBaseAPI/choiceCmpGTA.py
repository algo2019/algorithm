from choiceDB import choiceDB
from GTADB import GTADB
from datetime import datetime
cdb = choiceDB()
cdb.start()
cConf = {}
cConf['start'] = datetime(2015,01,01,00,00,00)
cConf['end'] = datetime(2015,12,01,00,00,00)
cConf['fildes'] = 'OPEN,HIGH,LOW,NEW'
cConf['adj'] = '0'
cConf['orderBy'] = 'TRADEDATE,SECURITYCODE'


gdb = GTADB()
gdb.start()
gConf = {}
gConf['start'] = datetime(2015,01,01,00,00,00)
gConf['end'] = datetime(2015,12,31,00,00,00)
gConf['fildes'] = 'OPENPRICE,HIGHPRICE,LOWPRICE,CLOSEPRICE'
gConf['adj'] = '0'
gConf['orderBy'] = 'TRADINGDATE,SYMBOL'

print 'choiceDB query start'
cdata = cdb.getStockDaily(cConf)
print 'choiceDB query over'
print 'GTADB query start'
gdata = gdb.getStockDaily(gConf)
print 'GTADB query over'

ci = 0
gi = 0

c = 0
sum4 = 0
while ci < len(cdata) and gi<len(gdata):
	if c%1000 == 0 and not c:
		print 'date:%s c:%d'%(cdata[ci][0].date(),c)

	if cdata[ci][0].date() < gdata[gi][0].date():
		ci += 1
	elif cdata[ci][0].date() > gdata[gi][0].date():
		gi += 1
	elif cdata[ci][1] < gdata[gi][1]:
		ci += 1
	elif cdata[ci][1] > gdata[gi][1]:
		gi += 1
	else:
		s = 0
		for i in range(2,6):
			s += abs(cdata[ci][i] - gdata[gi][i])
		c += 1
		sum4 += s/4
		ci += 1
		gi += 1

print 'stock:%d\nsum4:%f\nargv:%f'%(c,sum4,sum4/c)