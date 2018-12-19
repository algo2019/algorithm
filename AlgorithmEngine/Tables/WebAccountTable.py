# coding=utf-8
import abc

from Common.Dao.ConfigDao import ConfigDao
import hashlib
__all__ = ['WebAccountTable', 'create', 'BasePassWordStrategy']


class BasePassWordStrategy(object):
    @abc.abstractmethod
    def process(self, username, password):
        raise NotImplemented

    def __call__(self, *args, **kwargs):
        return self.process(*args, **kwargs)


class MD5PassWordStrategy(BasePassWordStrategy):
    def process(self, username, password):
        h = hashlib.md5()
        h.update(str(username))
        h.update(str(password))
        return repr(h.digest())


class WebAccountTable(object):
    admin = 'admin'
    user_mgr = 'usermgr'
    online_opr = 'onlineoper'
    user = 'user'
    user2 = 'user2'
    online_opr2 = 'onlineoper'
    login = 'login'
    dev = 'dev'

    # 1 2 4 8
    # 0x00000000
    _role_table = {
        # 'none': 0x00000000,
        'login': 0x10000000,  # 允许登录
        'admin': 0xFFFFFFFF,  # 所有权限
        'user': 0x00000001,  # 查看1类账户
        'onlineoper': 0x00000002,  # 线上操作1类账户
        'usermgr': 0x80000000,  # 用户管理
        'user2': 0x00000010,  # 查看2类账户
        'onlineoper2': 0x00000020,  # 线上操作2类账户
        'dev': 0x20000000,  # 开发者
    }

    def __init__(self):
        self._prefix = 'WebAccount.'
        self.__db = ConfigDao(self._prefix)
        self.__pw_strategy = MD5PassWordStrategy()

    def set_pass_word_strategy(self, strategy):
        self.__pw_strategy = strategy

    def insert_user(self, username, password='123456', role='none', bossname='', email='', cellphone=''):

        self.__db.set_map(username, {
            'username': username,
            'password': self.__pw_strategy(username, password),
            'role': self._in_role(role),
            'bossname': bossname,
            'email': email,
            'cellphone': cellphone
        })

    def change_password(self, username, old, new):
        if not self.check_password(username, old):
            return False

        self.__db.set(username, 'password', self.__pw_strategy(username, new))
        return True

    def check_password(self, username, password):
        if self.__db.get(username, 'password') == self.__pw_strategy(username, password):
                return True
        return False

    def check_user(self, username):
        return {'username', 'password', 'role', 'bossname', 'email', 'cellphone'} == \
               set(self.__db.select_sys(username).keys())

    def update_msg(self, username, role='none', bossname='', email='', cellphone=''):
        self.__db.set_map(username, {
            'role': self._in_role(role),
            'bossname': bossname,
            'email': email,
            'cellphone': cellphone
        })

    def get_all(self):
        a = self.__db.select_all()
        return [(a[key]['username'],
                 self._rt_role(a[key]['role']),
                 a[key]['bossname'],
                 a[key]['email'],
                 a[key]['cellphone']) for key in a]

    def _rt_role(self, role):
        rt = []
        if isinstance(role, basestring):
            role = int(role)
        for role_str in self._role_table:
            if role | self._role_table[role_str] == role:
                rt.append(role_str)
        return ','.join(rt)

    def _in_role(self, role_strs):
        role_strs = role_strs.split(',')
        role = 0x0
        for role_str in role_strs:
            role = self._role_table.get(role_str, 0) | role
        return role

    def get_data(self, username=None, role=None, bossname=None, email=None, cellphone=None):
        f = {}
        if bossname is not None:
            f['bossname'] = role
        if email is not None:
            f['email'] = role
        if cellphone is not None:
            f['cellphone'] = role
        a = self.__db.get_all(username)

        r = []
        for ac in a.values():
            if not (role is not None and self.has_role(ac['username'], role)):
                continue

            c = 1
            for k in f:
                if ac[k] != f[k]:
                    c = 0
                    break
            if c:
                r.append(ac)
        return [(ac['username'], self._rt_role(ac['role']), ac['bossname'], ac['email'], ac['cellphone']) for ac in r]

    def get_all_username(self):
        a = self.__db.select_all()
        return [a[k]['username'] for k in a]

    def is_admin(self, username):
        return self.has_role(username, self.admin)

    def is_user_mgr(self, username):
        return self.has_role(username, self.user_mgr)

    def is_online_opr(self, username):
        return self.has_role(username, self.online_opr)

    def get_all_role(self):
        return self._role_table.keys()

    def get_role(self, username):
        return self._rt_role(self.__db.get(username, 'role'))

    def has_role(self, username, role_str):
        role = int(self.__db.get(username, 'role'))
        return role | self._in_role(role_str) == role

    @staticmethod
    def __get_list_str(_list):
        return "('" + "','".join(_list) + "')"

    def get_boss(self, users):
        a = self.__db.get_all()
        boss = set()
        users = set(users)
        for ac in a.values():
            if ac['username'] in users:
                boss = boss | set(ac['bossname'].split(','))
        return boss

    def get_underline(self, bosses):
        a = self.__db.get_all()
        underline = set()
        bosses = set(bosses)
        for ac in a.values():
            if len(set(ac['bossname'].split(',')) & bosses) > 0:
                underline.add(ac['username'])
        return underline

    def get_all_underline(self, boss):
        c = -1
        rt = {boss}
        while c != len(rt):
            c = len(rt)
            rt = rt.union(self.get_underline(rt))
        return list(rt)

    def delete(self, username):
        self.__db.delete(username)

    def get_access_system_type(self, username):
        rt = set()
        if self.has_role(username, self.user):
            rt.add('1')
        if self.has_role(username, self.user2):
            rt.add('2')
        if self.has_role(username, self.dev):
            rt.add('0')
        return rt


def create():
    return WebAccountTable()
