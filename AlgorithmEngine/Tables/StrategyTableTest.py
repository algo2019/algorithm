import unittest
from StrategyTable import create
from Common.Dao.ConfigDao import Config


class StrategyTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = Config.REDIS_HOST
        Config.REDIS_HOST = '10.4.37.206'
        cls.u1 = 'user1'
        cls.u2 = 'user2'

        cls.s1 = 'strategy1'
        cls.s2 = 'strategy2'
        cls.s22 = 'strategy22'

        cls.pk1 = 'pk1'
        cls.pk2 = 'pk2'

    @classmethod
    def tearDownClass(cls):
        Config.REDIS_HOST = cls.old

    def setUp(self):
        self.st = create()
        self.st.insert(self.pk1, self.s1, self.u1)
        self.st.insert(self.pk1, self.s2, self.u2)
        self.st.insert(self.pk1, self.s22, self.u2)
        self.st.insert(self.pk2, self.s22, self.u2)

    def tearDown(self):
        self.st.delete(self.pk1, self.s1)
        self.st.delete(self.pk1, self.s2)
        self.st.delete(self.pk1, self.s22)
        self.st.delete(self.pk2, self.s22)

    def test_get_strategy_of_user(self):
        self.assertListEqual(self.st.get_strategy_of_user(self.pk1, [self.u1]), [self.s1])
        self.assertListEqual(self.st.get_strategy_of_user(self.pk1, [self.u2]), [self.s22, self.s2])
        self.assertListEqual(self.st.get_strategy_of_user(self.pk1, [self.u1, self.u2]), ['strategy22', 'strategy2', 'strategy1'])
        self.assertListEqual(self.st.get_strategy_of_user(self.pk2, [self.u1, self.u2]), ['strategy22'])

    def test_get_strategy_info_of_user(self):
        self.assertListEqual(self.st.get_strategy_info_of_user(self.pk2, [self.u2]), [('strategy22', 'pk2', 'user2', '')])
        self.assertListEqual(self.st.get_strategy_info_of_user(self.pk1, [self.u2]), [('strategy22', 'pk1', 'user2', ''), ('strategy2', 'pk1', 'user2', '')])

    def test_check_strategy(self):
        self.assertTrue(self.st.check_strategy(self.pk1, self.s1))
        self.assertFalse(self.st.check_strategy(self.pk2, self.s1))

    def test_update_path(self):
        self.st.update_path(self.pk1, self.s1, '123')
        self.assertEqual(self.st.get_start_conf(self.pk1, self.s1), ('123', ))
        self.assertEqual(self.st.get_start_conf(self.pk1, self.s2), ('', ))

    def update_user(self):
        self.st.update_user(self.pk1, self.s1, self.s2)
        self.assertListEqual(self.st.get_strategy_of_user(self.pk1, self.u2), ['strategy22', 'strategy2', 'strategy1'])

    def test_get_strategy_of_sys(self):
        self.assertListEqual(self.st.get_strategy_of_sys(self.pk1), ['strategy22', 'strategy2', 'strategy1'])

    def test_get_start_conf_of_sys(self):
        self.assertListEqual(self.st.get_start_conf_of_sys(self.pk1), [('strategy22', ''), ('strategy2', ''), ('strategy1', '')])

    def test_get_start_conf(self):
        self.assertTupleEqual(self.st.get_start_conf(self.pk1, self.s1), ('', ))

    def test_get_all_data(self):
        self.assertListEqual(self.st.get_all_data(strategy=self.s1), [('strategy1', 'pk1', 'user1', '')])
        self.assertListEqual(self.st.get_all_data(publish_key=self.pk1), [('strategy22', 'pk1', 'user2', ''), ('strategy2', 'pk1', 'user2', ''), ('strategy1', 'pk1', 'user1', '')])
        self.assertListEqual(self.st.get_all_data(publish_key=self.pk1, username=self.u2), [('strategy22', 'pk1', 'user2', ''), ('strategy2', 'pk1', 'user2', '')])
