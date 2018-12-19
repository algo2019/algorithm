# -*- coding:utf-8 -*-

import dataBase
import sqlBuilder

#choice 数据库
class choiceDB(dataBase.mysqlDataBase):
    def __init__(self,dbName='test'):
        self.__HOST = '10.4.27.173'
        self.__PORT = 3306
        self.__USER = 'tango_devo'
        self.__PASSWD = '123456'
        self.__sql = sqlBuilder.sqlBuilder()

        dataBase.mysqlDataBase.__init__(self,self.__HOST,self.__PORT,self.__USER,self.__PASSWD,dbName)
    def __TRAD_SK_DAILY_JC__(self,conf):
        conf['tableName'] = 'TRAD_SK_DAILY_JC'
        conf['dateName'] = 'TRADEDATE'
        conf['codeName'] = 'SECURITYCODE'
        return self.runSql(self.__sql.build(conf))

    def getStockDaily(self,conf):
        if conf['adj'] == '0':
            return self.__TRAD_SK_DAILY_JC__(conf)
        else:
            raise Exception('adj not supprt')


#test 
def printRow(data):
    for line in data:
        print line
def test():
    from datetime import datetime
    cdb = choiceDB()
    cdb.start()
    conf = {}
    #conf['code'] = ['000001','000002']
    #conf['start'] = datetime(2016,04,01,00,00,00)
    conf['end'] = datetime(2016,10,10,00,00,00)
    conf['fildes'] = 'TRADEDATE' #'OPEN,HIGH,LOW,NEW'
    #conf['orderBy'] = 'TRADEDATE'
    conf['adj'] = '0'
    conf['groupBy'] = 'TRADEDATE'

    printRow(cdb.getStockDaily(conf))

if __name__ == '__main__':
    test()
