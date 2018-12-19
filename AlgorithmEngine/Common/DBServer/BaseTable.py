
class Table(object):
    def __init__(self, name):
        self.name = name
        self._db = self.get_db()

    def get_db(self):
        raise NotImplementedError

    def exists(self):
        self._db.execute("select count(*) c from sqlite_master where type=? and name=?", ['table', self.name])
        one = self._db.fetchone()
        if one[0] > 0:
            return True
        return False

    def drop(self):
        self._db.execute("drop table %s" % self.name)
        self._db.commit()

    def __iter__(self):
        rt = self._db.fetchone()
        while rt:
            yield rt

    def run_sqls(self, sqls, *args, **kwargs):
        if type(sqls) in {str, unicode}:
            sqls = [sqls]
        for sql in sqls:
            self._db.execute(sql, *args)
        self._db.commit()
        if not kwargs.get('res', True):
            return
        if kwargs.get('iter', False):
            return self

        return self._db.fetchall()
