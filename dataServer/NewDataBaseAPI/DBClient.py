# -*- coding:utf-8 -*-

import pyodbc


class DBClient(object):
    DEFAULT_USER = ('research', 'rI2016')

    def __init__(self):
        self.__host = '10.4.27.179'
        self.__port = 1433
        self.__user, self.__passwd = self.DEFAULT_USER
        self.__connect = None
        self.__cursor = None

    def open(self, db_name='tempdb'):
        self.__connect = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=%s;port=%s;UID=%s;PWD=%s;DATABASE=%s;TDS_Version=8.0' % (
                self.__host, self.__port, self.__user, self.__passwd, db_name))
        self.__cursor = self.__connect.cursor()

    def close(self):
        self.__connect.close()
        self.__cursor.close()

    def run_sql(self, cmd_or_cmds, res=True):
        if type(cmd_or_cmds) in {str, unicode}:
            cmds = [cmd_or_cmds]
        else:
            cmds = cmd_or_cmds
        for cmd in cmds:
            self.__cursor.execute(cmd)
        if res:
            return self.__cursor.fetchall()

    def commit(self):
        self.__cursor.commit()

    def db_run_sql(self, db, cmd_or_cmds, res=True):
        db_sql = "use {};".format(db)
        if type(cmd_or_cmds) in {str, unicode}:
            cmds = [db_sql, cmd_or_cmds]
        else:
            cmds = [db_sql] + list(cmd_or_cmds)
        return self.run_sql(cmds, res)
