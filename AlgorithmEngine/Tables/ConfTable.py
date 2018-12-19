from Common.Dao.ConfigDao import ConfigDao

__all__ = ['create', 'ConfTable']


class ConfTable(object):
    DEFAULT = ConfigDao.DEFAULT

    def __init__(self):
        self.__db = ConfigDao('ConfTable')

    def set(self, publish_key, conf_name, conf_value):
        self.__db.set_map(publish_key, {conf_name: conf_value, '__pk__': publish_key})

    def set_map(self, publish_key, mapping):
        mapping['__pk__'] = publish_key
        self.__db.set_map(publish_key, mapping)

    def delete(self, publish_key, conf_name=None):
        self.__db.delete(publish_key, conf_name)

    def select_all(self):
        rt = []
        for conf_obj in self.__db.select_all().values():
            pk = conf_obj['__pk__']
            for key in conf_obj:
                if key.startswith('__') and key.endswith('__'):
                    continue
                rt.append((pk, key, conf_obj[key]))
        return rt

    def select_sys(self, publish_key):
        return self.__db.select_sys(publish_key)

    def select_conf(self, publish_key, conf_name):
        rt = self.__db.select_conf(publish_key, conf_name)
        if rt is not None:
            return rt
        return self.__db.select_conf(self.DEFAULT, conf_name)

    def get_conf(self, publish_key):
        return self.__db.get_conf(publish_key)


def create():
    return ConfTable()
