import unittest
from ConfTable import create
from Common.Dao.ConfigDao import Config


class ConfTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = Config.REDIS_HOST
        Config.REDIS_HOST = '10.4.37.206'

    @classmethod
    def tearDownClass(cls):
        Config.REDIS_HOST = cls.old

    def setUp(self):
        self.pk1 = 'pk1'
        self.pk2 = 'pk2'
        self.n1 = 'name1'
        self.n2 = 'name2'
        self.v1 = 'vvvvv`'
        self.v2 = 'vvvvv2'

        self.ct = create()
        self.ct.set_map(self.pk1, {
            self.n1: self.v1,
            self.n2: self.v2
        })
        self.ct.set(self.pk2, self.n1, self.v2)
        self.ct.set(self.ct.DEFAULT, self.n2, self.v1)

    def tearDown(self):
        self.ct.delete(self.pk2)
        self.ct.delete(self.pk1)
        self.ct.delete(self.ct.DEFAULT)

    def test_set(self):
        self.assertListEqual(self.ct.select_all(), [('pk2', 'name1', 'vvvvv2'), ('pk1', 'name2', 'vvvvv2'), ('pk1', 'name1', 'vvvvv`'), ('DEFAULT', 'name2', 'vvvvv`')])

    def test_delete(self):
        self.ct.delete(self.pk1)
        self.assertListEqual(self.ct.select_all(), [('pk2', 'name1', 'vvvvv2'), ('DEFAULT', 'name2', 'vvvvv`')])

    def test_select_sys(self):
        self.assertDictEqual(self.ct.select_sys(self.pk1), {'name2': 'vvvvv2', '__pk__': 'pk1', 'name1': 'vvvvv`'})
        self.assertDictEqual(self.ct.select_sys(self.pk2), {'name1': 'vvvvv2', '__pk__': 'pk2'})

    def test_select_conf(self):
        self.assertEqual(self.ct.select_conf(self.pk2, self.n2), self.ct.select_conf(self.ct.DEFAULT, self.n2))
        self.assertEqual(self.ct.select_conf(self.pk1, self.n2), 'vvvvv2')

    def test_get_conf(self):
        self.assertDictEqual(self.ct.get_conf(self.pk1), {'name2': 'vvvvv2', '__pk__': 'pk1', 'name1': 'vvvvv`'})
        self.assertDictEqual(self.ct.get_conf(self.pk2), {'name2': 'vvvvv`', '__pk__': 'pk2', 'name1': 'vvvvv2'})
        self.assertDictEqual(self.ct.get_conf(self.ct.DEFAULT), {'name2': 'vvvvv`', '__pk__': 'DEFAULT'})