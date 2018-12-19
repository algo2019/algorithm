from dataServer.LocalDataServer.DBApi import Conf
from dataServer.LocalDataServer.DBApi.Tables import DomInfoTable
Conf.DB_PATH = '/Users/renren1/test/LocalData.db'

d = DomInfoTable()
dom_sql = 'select * from {}'.format(d.name)
d.open()
# for line in d.run_sqls(dom_sql, iter=True):
#     print line
for line in d.select('bu', '20100101', '20160101'):
    print line
