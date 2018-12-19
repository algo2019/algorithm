import MySqlDao
import time

from tools import format_to_datetime as dt_format


class TradeRecordDao(MySqlDao.MySqlDao):
    def __init__(self):
        super(TradeRecordDao, self).__init__()
        self.__table_name = 'Algorithm'

    def create(self):
        sql = '''CREATE TABLE IF NOT EXISTS {} (
                    system VARCHAR(20),
                    strategy VARCHAR(20),
                    date DATE,
                    time TIME,
                    instrument VARCHAR(20),
                    offset CHAR(1),
                    direction CHAR(1),
                    order_volume INT(4),
                    filled_volume INT(4),
                    price DOUBLE(10, 2));'''.format(self.__table_name)
        self.run_sqls(sql, res=False)

    def put_trade(self, system, strategy, datetime, instrument, offset, direction, order_volume, filled_volume, price):
        dt = dt_format(datetime, ms=False)
        sql = '''insert into {} (
                    system, strategy, date, time, instrument, offset, direction, order_volume, filled_volume, price
                ) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(
            self.__table_name,
            system, strategy, dt.date(), dt.time(), instrument, offset, direction, order_volume, filled_volume, price
        )
        try:
            self.run_sqls(sql, res=False)
            self._conn.commit()
        except:
            raise

    def get_days(self, system, strategy):
        sql = '''select date from {}
                    where system = '{}' and strategy = '{}'
                    group by date;'''.format(self.__table_name, system, strategy)
        return [x[0] for x in self.run_sqls(sql)]

    def get_by_day(self, system, strategy, date):
        sql = '''select time, instrument, offset, direction, order_volume, filled_volume, price from {}
                    where system = '{}' and strategy = '{}' and date = '{}' ;
                    '''.format(self.__table_name, system, strategy, dt_format(date, time=False))
        return self.run_sqls(sql)
