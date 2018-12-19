# -*- coding:utf-8 -*-
# 数据库基类
class dataBase(object):
    def __int__(self):
        self.__started = False

    def start(self, conn):
        self.__conn = conn
        self.__cursor = self.__conn.cursor()
        self.__started = True

    def stop(self):
        self.__cursor.close()
        self.__conn.close()
        self.__started = False

    def close(self):
        self.stop()

    def __del__(self):
        try:
            self.stop()
        except:
            pass

    def runSqls(self, cmds, res=True):
        for cmd in cmds:
            self.runSql(cmd, False)
        if res:
            return self.__cursor.fetchall()

    def commit(self):
        self.__cursor.commit()

    def runSql(self, cmd, res=True):
        print cmd
        self.__cursor.execute(cmd)
        print 'dataBase cursor execute ok'
        if res:
            return self.__cursor.fetchall()

    def dbRunSql(self, dbName, cmd, res=True):
        return self.runSqls(["use %s;" % (dbName), cmd], res)


# mysql 数据库
class mysqlDataBase(dataBase):
    def __init__(self, host, port, user, passwd, dbName, charset='utf8'):
        dataBase.__init__(self)
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__dbName = dbName
        self.__charset = charset

    def start(self):
        import MySQLdb
        dataBase.start(self, MySQLdb.connect(host=self.__host, user=self.__user, passwd=self.__passwd, db=self.__dbName,
                                             charset=self.__charset))


# sqlserver 数据库
class sqlServerDataBase(dataBase):
    def __init__(self, host, port, user, passwd, dbName, charset='utf8'):
        dataBase.__init__(self)
        self.__host = host
        self.__port = port
        self.__started = False
        self.setUser(user, passwd)
        self.__dbName = dbName
        self.__charset = charset

    def setUser(self, user, passwd):
        self.__user = user
        self.__passwd = passwd

    def start(self):
        if not self.__started:
            self.__started = True
            import pyodbc
            dataBase.start(self, pyodbc.connect(
                "DRIVER={SQL Server};SERVER=%s;port=%s;UID=%s;PWD=%s;DATABASE=%s;TDS_Version=8.0" % (
                    self.__host, self.__port, self.__user, self.__passwd, self.__dbName)))
