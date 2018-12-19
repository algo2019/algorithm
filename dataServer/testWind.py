from dataServer import dataServer, Conf
Conf.CACHE = False


d = dataServer('10.2.53.13')

d.start()

res = d.wsi('SR705.CZC', 'close', '2016-12-30', '2017-01-01 10:00:00')

for i in range(len(res.Data[0])):
    if res.Data[0][i] == res.Data[0][i]:
        print res.Times[i]