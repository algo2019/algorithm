from dataBaseAPI.dataBase.GTADB import GTADB

GTADB.defaultUser = lambda x: ('gta_updata', 'rI2016')

def run():
    db = GTADB()
    db.start()
    sql = "select TDATETIME,CONTRACTID,MINQTY from MFL1_TRDMIN05_201606  where  TDATETIME>='2016-07-01 00:00:00'  and  TDATETIME<'2016-07-01 00:01:00' order by CONTRACTID"
    for line in db.dbRunSql('GTA_MFL1_TRDMIN_201606', sql):
        print line

    sql = "select TDATETIME,CONTRACTID,MINQTY from MFL1_TRDMIN05_201607  where  TDATETIME>='2016-07-01 00:00:00'  and  TDATETIME<'2016-07-01 00:01:00' order by CONTRACTID"
    for line in db.dbRunSql('GTA_MFL1_TRDMIN_201607', sql):
        print line


    db.close()

def test():
    from dataBaseAPI.dataBaseClient import Client

    c = Client()
    config = {
        'dataName': 'data',
        'period': '5m',
        'code': 'ag1706',
        'start': '2016-07-01 00:00:00',
        'end': '2016-07-01 00:01:00',
    }

    c.start()
    for line in c.wmm(config):
        print line
    c.stop()


run()