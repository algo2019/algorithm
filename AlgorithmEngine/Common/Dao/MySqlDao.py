
import MySQLdb
import time


class _MySqlDao(object):
    def __init__(self, host, port, user, passwd):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__db_name = 'TradeRecord'
        self.__conn = None
        self.__cursor = None
        self.__last_op = None
        self.__timeout = 100

    def __del__(self):
        self._close()

    @property
    def _conn(self):
        return self.__conn

    def __check_timeout(self):
        if self.__last_op is None or time.time() - self.__last_op > self.__timeout:
            self._close()
            self._connect()

    def _connect(self):
        self.__conn = MySQLdb.connect(host=self.__host, user=self.__user, passwd=self.__passwd, db=self.__db_name)
        self.__cursor = self.__conn.cursor()

    def run_sqls(self, sql_or_sqls, res=True, use_iter=False):
        self.__check_timeout()
        self.__last_op = time.time()
        if type(sql_or_sqls) in (str, unicode):
            sql_or_sqls = [sql_or_sqls]
        sqls = ['use {};'.format(self.__db_name)] + sql_or_sqls
        for sql in sqls:
            self.__cursor.execute(sql)
        if res:
            if not use_iter:
                return self.__cursor.fetchall()
            else:
                return self.__cursor

    def commit(self):
        self._conn.commit()

    def _close(self):
        try:
            self.__cursor.close()
            self.__conn.close()
        except:
            pass

    def mul_values(self, values):
        return "('" + "','".join(map(lambda x: str(x) if x is not None else 'null', values)) + "')"

    def insert_values(self, table, cols, values):
        sql = "INSERT INTO {} ({}) VALUES ".format(
            table, ','.join(cols))
        remain = values
        try:
            while len(remain) > 0:
                this_time = remain[:1000]
                remain = remain[1000:]
                this_sql = sql + ",".join(map(lambda x: self.mul_values(x), this_time))
                self.run_sqls(this_sql, False)
            self.commit()
        except Exception as e:
            self.__conn.rollback()
            raise


class MySqlDao(_MySqlDao):
    def __init__(self):
        try:
            import package_config
            import os
            if os.path.exists(package_config.config_file):
                with open(package_config.config_file) as f:
                    import json
                    config = json.loads(f.read())['mysql_server']
                    host = config['host']
                    port = config['port']
                    user = config['user']
                    passwd = config['password']
                print 'MySqlDao: load config from', package_config.config_file
            else:
                raise Exception('{} not found'.format(package_config.config_file))
        except Exception as e:
            print 'MySqlDao: sql server load config file err:', str(e)
            print 'MySqlDao: sql server user default config'
            host = '10.4.27.181'
            port = 3306
            user = 'finance'
            passwd = 'renren2017'

        super(MySqlDao, self).__init__(host, port, user, passwd)
