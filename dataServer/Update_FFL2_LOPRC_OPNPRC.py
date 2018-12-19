import pyodbc

import datetime


def add_months(dt, months):
    targetmonth = months + dt.month
    try:
        dt = dt.replace(year=dt.year + int(targetmonth / 12), month=(targetmonth % 12))
    except:
        dt = dt.replace(year=dt.year + int((targetmonth + 1) / 12), month=((targetmonth + 1) % 12), day=1)
        dt += datetime.timedelta(days=-1)
    return dt


class DataBase(object):
    def __init__(self):
        self.minute_list = ["01"]
        self.start = datetime.datetime(2013, 10, 1)
        self.end = datetime.datetime(2013, 10, 1)
        self.db_per_fix = "GTA_FFL2_TRDMIN_{}"
        self.conn = None
        self.cursor = None

    def connect(self, date_time):
        self.conn = pyodbc.connect(
            "DRIVER={{SQL Server}};SERVER=10.4.27.179;port=1433;UID=gta_updata;PWD=rI2016;DATABASE={};TDS_Version=8.0" \
                .format(self.db_per_fix.format(date_time.strftime('%Y%m'))))
        self.cursor = self.conn.cursor()

    def sql(self, cmd):
        self.cursor.execute(cmd)
        return self.cursor.fetchall()

    def update(self, table):
        cmd = "update {} set LOPRC = OPNPRC where OPNPRC < LOPRC".format(table)
        self.cursor.execute(cmd)
        self.cursor.commit()

    def select(self, table):
        cmd = "select * from {} where OPNPRC < LOPRC".format(table)
        self.cursor.execute(cmd)
        # self.cursor.commit()
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def run(self):
        dt = self.start
        while dt <= self.end:
            self.connect(dt)
            for minute in self.minute_list:
                table = "FFL2_TRDMIN%s_%s" % (minute, dt.strftime('%Y%m'))
                print "table#{}".format(table)
                print 'up-', self.select(table)
                self.update(table)
                print 'up+', self.select(table)

            self.close()
            dt = add_months(dt, 1)


t = DataBase()

t.run()
