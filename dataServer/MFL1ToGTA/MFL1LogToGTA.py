import sys

from External.GTADBOperator import GTADBOperator

db = GTADBOperator()
if __name__ == '__main__':
    sql = ''
    use = ''
    db.start()

    for line in sys.stdin:
        ds = line.strip().split()
        if  ds[0] == 'use':
            use = line.strip()
        elif ds[0] == 'insert':
            sql = line.strip()
        elif ds[0] == "('23000',":
            try:
                db.runSqls([use, sql], False)
                db.commit()
            except Exception, e:
                print e
                ds = sql.split("'")
                ws = ds[0].split()
                delsql = "delete from %s where CONTRACTID='%s' and TDATETIME='%s';"%(ws[2], ds[1], ds[3])
                db.runSqls([use, delsql], False)
                db.commit()
                db.runSqls([use, sql], False)
                db.commit()

    db.stop()
