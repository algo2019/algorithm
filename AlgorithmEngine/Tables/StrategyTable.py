from Common.Dao.ConfigDao import ConfigDao


class StrategyTable(object):
    def __init__(self):
        self.__db = ConfigDao('StrategyTable.')

    @staticmethod
    def _key(pk, sn):
        return '{}.{}'.format(pk, sn)

    def insert(self, publish_key, strategy, username, strategy_path=''):
        self.__db.set_map(self._key(publish_key, strategy), {
            'pk': publish_key,
            'strategy': strategy,
            'username': username,
            'strategy_path': strategy_path
        })

    def _get_all(self, pk):
        return self.__db.get_all(self._key(pk, '*')).values()

    def get_strategy_of_user(self, publish_key, usernames):
        usernames = set(usernames)
        return [x['strategy'] for x in self._get_all(publish_key) if x['username'] in usernames]

    def get_strategy_info_of_user(self, publish_key, usernames):
        usernames = set(usernames)
        return [(x['strategy'], x['pk'], x['username'], x['strategy_path'])
                for x in self._get_all(publish_key) if x['username'] in usernames]

    def check_strategy(self, pk, strategy):
        return len(self.__db.get_all(self._key(pk, strategy))) == 4

    def update_path(self, publish_key, strategy, strategy_path=''):
        self.__db.set(self._key(publish_key, strategy), 'strategy_path', strategy_path)

    def update_user(self, publish_key, strategy, username):
        self.__db.set(self._key(publish_key, strategy), 'username', username)

    def get_strategy_of_sys(self, publish_key):
        return [x['strategy'] for x in self._get_all(publish_key)]

    def get_start_conf_of_sys(self, publish_key):
        return [(x['strategy'], x['strategy_path']) for x in self._get_all(publish_key)]

    def get_start_conf(self, publish_key, strategy):
        return self.__db.get(self._key(publish_key, strategy), 'strategy_path'),

    def delete(self, publish_key, strategy, username=None):
        self.__db.delete(self._key(publish_key, strategy))

    @staticmethod
    def get_unique_key(publish_key, strategy):
        return 'Unique.%s.%s' % (publish_key, strategy)

    def get_all_data(self, strategy=None, publish_key=None, username=None):
        fs = {}
        if strategy is not None:
            fs['strategy'] = strategy
        if publish_key is not None:
            fs['pk'] = publish_key
        if username is not None:
            fs['username'] = username
        rt = []
        for si in self.__db.get_all().values():
            f = True
            for key in fs:
                if fs[key] != si[key]:
                    f = False
                    break
            if f:
                rt.append(si)
        return [(x['strategy'], x['pk'], x['username'], x['strategy_path']) for x in rt]


def create():
    return StrategyTable()
