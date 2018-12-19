from Common.Dao.ConfigDao import ConfigDao


class PublishKey(object):
    type = 'type'
    lab = 'lab'
    state = 'state'
    id = 'id'

    def __init__(self):
        self.__db = ConfigDao('PublishKeyTable.')

    def insert(self, publish_key, lab='', state='0', type='0', id=None):
        self.__db.set_map(publish_key, {
            'pk': publish_key,
            'lab': lab,
            'state': state,
            'type': type,
            'id': id or self._next_id(),
        })

    def delete(self, publish_key):
        self.__db.delete(publish_key)

    def select_all(self):
        return [x['pk'] for x in self.__db.get_all().values()]

    def get_all_data(self):
        return [(x['pk'], x['lab'], x['state'], x['type'])
                for x in sorted(self.__db.get_all().values(), key=lambda y: int(y.get('id', 100)))]

    def _next_id(self):
        return max([int(x.get('id', 0)) for x in self.__db.get_all().values()]) + 1

    def get_data(self, publish_key):
        x = self.__db.get_all(publish_key)
        return x['pk'], x['lab'], x['state'], x['type']

    def get_state(self, publish_key):
        return self.__db.get(publish_key, 'state')

    def get_type(self, publish_key):
        return self.__db.get(publish_key, 'type')

    def get_id(self, pulish_key):
        return self.__db.get(pulish_key, 'id')

    def set(self, publish_key, conf_name, value):
        self.__db.set(publish_key, conf_name, value)


def create():
    return PublishKey()
