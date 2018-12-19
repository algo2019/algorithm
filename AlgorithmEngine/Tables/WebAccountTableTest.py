from Common.Dao.ConfigDao import Config
from WebAccountTable import create
import unittest


class NewWebAccountTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = Config.REDIS_HOST
        cls.username = 'unittest'
        Config.REDIS_HOST = '10.4.37.206'

    @classmethod
    def tearDownClass(cls):
        Config.REDIS_HOST = cls.old

    def setUp(self):
        self.wt = create()
        self.wt.insert_user(self.username, '888888', 'user,admin')

    def tearDown(self):
        self.wt.delete(self.username)

    def test_insert(self):
        self.assertListEqual(self.wt.get_all(),
                             [('unittest', 'usermgr,onlineoper,user2,admin,onlineoper2,user', '', '', '')])

    def test_change_password(self):
        self.wt.change_password(self.username, '888888', 765311235)
        self.assertTrue(self.wt.check_password(self.username, '765311235'))

    def test_check_password(self):
        self.assertTrue(self.wt.check_password(self.username, '888888'))
        self.assertFalse(self.wt.check_password(self.username, '188888'))

    def test_check_user(self):
        self.assertTrue(self.wt.check_user(self.username))
        self.assertFalse(self.wt.check_user('*'))

    def test_update_msg(self):
        self.wt.update_msg(self.username, 'user,user2')
        self.assertListEqual(self.wt.get_all(),
                             [('unittest', 'user2,user', '', '', '')])

    def test_get_all(self):
        self.wt.insert_user('u2')
        self.assertListEqual(self.wt.get_all(), [('unittest', 'usermgr,onlineoper,user2,admin,onlineoper2,user', '',
                                                  '', ''), ('u2', '', '', '', '')])

        self.wt.delete('u2')

    def test_get_data(self):
        self.wt.insert_user('u2', role='user2')
        self.wt.insert_user('u3', role='user')
        self.assertListEqual(self.wt.get_data(role='user2'), [('unittest', 'usermgr,onlineoper,user2,admin,onlineoper2,user', '', '', ''), ('u2', 'user2', '', '', '')])
        self.wt.delete('u2')
        self.wt.delete('u3')

    def test_get_all_username(self):
        self.assertListEqual(self.wt.get_all_username(), ['unittest'])

    def test_is_admin(self):
        self.wt.insert_user('u2', role='user2')
        self.assertFalse(self.wt.is_admin('u2'))
        self.assertTrue(self.wt.is_admin(self.username))
        self.wt.delete('u2')

    def test_is_user_mgr(self):
        self.wt.insert_user('u2', role='user2')
        self.assertFalse(self.wt.is_user_mgr('u2'))
        self.assertTrue(self.wt.is_user_mgr(self.username))
        self.wt.delete('u2')

    def test_is_online_opr(self):
        self.wt.insert_user('u2', role='user2')
        self.assertFalse(self.wt.is_online_opr('u2'))
        self.assertTrue(self.wt.is_online_opr(self.username))
        self.wt.delete('u2')

    def test_get_all_role(self):
        self.assertListEqual(self.wt.get_all_role(), ['usermgr', 'onlineoper', 'user2', 'admin', 'onlineoper2', 'user'])

    def test_get_role(self):
        self.assertEqual(self.wt.get_role(self.username), 'usermgr,onlineoper,user2,admin,onlineoper2,user')

    def test_has_role(self):
        self.assertTrue(self.wt.has_role(self.username, self.wt.admin))

    def test_get_boss_underline(self):
        self.wt.insert_user('u2', role='user2', bossname='{},{}'.format(self.username, 'u4'))
        self.wt.insert_user('u3', role='user2', bossname='u2')
        self.assertSetEqual(self.wt.get_boss(['u2']), {self.username, 'u4'})
        self.assertSetEqual(self.wt.get_boss(['u2', 'u3']), {'u2', self.username, 'u4'})
        self.assertSetEqual(self.wt.get_underline(['u2']), {'u3'})
        self.assertSetEqual(self.wt.get_underline(['u2', self.username]), {'u3', 'u2'})
        self.assertSetEqual(set(self.wt.get_all_underline(self.username)),  {'u3', 'u2', self.username})
        self.assertSetEqual(set(self.wt.get_all_underline('u2')),  {'u3', 'u2'})
        self.assertSetEqual(set(self.wt.get_all_underline('u4')), {'u4', 'u3', 'u2'})
        self.wt.delete('u2')
        self.wt.delete('u3')
