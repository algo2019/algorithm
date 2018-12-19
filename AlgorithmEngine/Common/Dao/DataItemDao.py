import MySqlDao
from tools import format_to_datetime as dt_format


class DataItemDao(MySqlDao.MySqlDao):
    def __init__(self):
        super(DataItemDao, self).__init__()
        self.__table_name = 'DataItem'

    @property
    def table_name(self):
        return self.__table_name

    def create(self):
        sql = '''CREATE TABLE IF NOT EXISTS {} (
                    system VARCHAR(20),
                    name VARCHAR(20),
                    item VARCHAR(20),
                    date DATE,
                    data DOUBLE(15, 2));'''.format(self.__table_name)
        self.run_sqls(sql, res=False)

    def put(self, system, name, item, date, data):
        sql = "insert into {} (system, name, item, date, data) values ('{}','{}','{}','{}','{}')".format(
            self.__table_name, system, name, item, dt_format(date, time=False), float(data)
        )
        self.run_sqls(sql, res=False)
        self._conn.commit()

    def get_all(self, system, name, item):
        sql = "select date, data from {} where system='{}' and name='{}' and item='{}' order by date".format(
            self.__table_name, system, name, item
        )
        return self.run_sqls(sql)

    def get_last(self, system, name, item):
        sql = "select date, data from {table} where date in (select max(date) from {table} where system='{system}' " \
              "and name='{name}' and item='{item}') and system='{system}' and name='{name}' and item='{item}'" \
              "".format(table=self.__table_name, system=system, name=name, item=item)
        rt = self.run_sqls(sql)
        if len(rt) > 0:
            return rt[0]
        return rt
