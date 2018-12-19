import unittest
from Common.Dao.ConfigDao import ConfigDao, Config

__all__ = ['ConfigDaoTest']


class ConfigDaoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = Config.REDIS_HOST
        Config.REDIS_HOST = '10.4.37.206'

    @classmethod
    def tearDownClass(cls):
        Config.REDIS_HOST = cls.old

    def setUp(self):
        self.dao =  ConfigDao()
        self.system = 'test'

    def tearDown(self):
        self.dao.delete(self.system)

    def test_key(self):
        Config.PREFIX = 'ck'
        dao = ConfigDao()
        self.assertEqual(dao.key('test'), 'cktest')
        Config.PREFIX = ''

    def test_set(self):
        self.dao.set(self.system, 'kkk', 123)
        self.assertEqual(self.dao.get(self.system, 'kkk'), '123')

    def test_set_map(self):
        d = {'1': '2', '2': '3'}
        self.dao.set_map(self.system, d)
        self.assertDictEqual(d, self.dao.get_all(self.system))

    def test_delete(self):
        d = {'1': '2', '2': '3'}
        self.dao.set_map(self.system, d)
        self.dao.delete(self.system, '1')
        self.assertDictEqual(self.dao.get_all(self.system), {'2': '3'})
        self.dao.delete(self.system)
        self.assertDictEqual(self.dao.get_all(self.system), {})

    def test_get_conf(self):
        self.dao.set(self.dao.DEFAULT, 'TTT', '123')
        self.assertDictEqual(self.dao.get_conf(self.system), {'TTT': '123'})
        self.dao.set(self.system, 'TTT', '234')
        self.dao.set(self.system, 'TT', '134')
        self.assertDictEqual(self.dao.get_conf(self.system), {'TTT': '234', 'TT': '134'})

