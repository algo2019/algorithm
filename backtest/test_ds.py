from dataServer import dataServer

d = dataServer()
d.start()
print d.wmm({
    'dataName': 'data',
    'start': '2018-01-01',
    'end': '2018-02-01',
    'code': 'A0',
    'period': '1d',
})
