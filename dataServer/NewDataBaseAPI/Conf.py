import threading
CACHE_DB_PATH = './cache.db'


class DB_TYPE(object):
    GTA = 'gta'
    SQLITE = 'sqlite'


def get_gta_db(type_=DB_TYPE.GTA, clear=False):
    lock = getattr(get_gta_db, 'lock')[type_]
    lock.acquire()
    d = getattr(get_gta_db, 'thread_dbs')[type_]
    empty_dbs = getattr(get_gta_db, 'empties')[type_]
    tid = threading._get_ident()
    if clear:
        d.pop(tid, None).close()
        return
    for not_active in set(d.keys()) - set(threading._active.keys()):
        empty_dbs.append(d.pop(not_active))

    if d.get(tid) is None:
        if len(empty_dbs) > 0:
            db = empty_dbs.pop()
        else:
            if type_ == DB_TYPE.GTA:
                from NewDataBaseAPI.DBClient import DBClient
                db = DBClient()
                db.open()
            elif type_ == DB_TYPE.SQLITE:
                import sqlite3
                db = sqlite3.connect(CACHE_DB_PATH, check_same_thread = False)
            else:
                raise Exception('DB type {} not define'.format(type_))
        d[tid] = db
    lock.release()
    return d[tid]

setattr(get_gta_db, 'thread_dbs', {DB_TYPE.GTA:{}, DB_TYPE.SQLITE: {}})
setattr(get_gta_db, 'empties', {DB_TYPE.GTA: [], DB_TYPE.SQLITE: []})
setattr(get_gta_db, 'lock', {DB_TYPE.GTA: threading.Lock(), DB_TYPE.SQLITE: threading.Lock()})
