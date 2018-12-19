from dataBaseAPI.dataBase.GTADB import GTADB


class GTADBOperator(GTADB):
    def __int__(self):
        GTADB.__init__(self)

    def defaultUser(self):
        return 'gta_updata', 'rI2016'

    def createDataBase(self, dbName):
        sql = 'create database %s' % (dbName)
        # self.runSql(sql)

    def createTable(self, dbName, tableName):
        sql = 'create table %s' % (tableName)
        # self.dbRunSql(dbName, sql)

    def insertValue(self, dbName, tableName, value):
        sql = "insert into %s values('%s')" % (tableName, "','".join(map(str, value)))
        self.dbRunSql(dbName, sql, False)
        self.commit()

    def insertValues(self, dbName, tableName, values):
        start = 0
        while len(values) - start > 0:
            end = min(start + 999, len(values))
            sql = "INSERT INTO %s values %s" % (tableName, "(" + "),(".join(values[start:end]) + ")")
            self.dbRunSql(dbName, sql, False)
            self.commit()
            start = end
