import unittest
from Common.HashDBAdapter.RedisDB import RedisDB

__all__ = ['HashDBTest']


class HashDBTest(unittest.TestCase):
    db = None

    def setUp(self):
        if self.db is None:
            self.db = RedisDB('10.4.37.206', 6379, 0)
        self.key = 'unittest'
        self.field = self.key + self.key

    def tearDown(self):
        self.db.delete(self.key)

    def test_delete(self):
        data = 'sdfdsfs'
        self.db.hset(self.key, self.field, data)
        self.db.delete(self.key)
        self.assertIsNone(self.db.hget(self.key, self.field))

    def test_hget_hset(self):
        data = '13242'
        self.db.hset(self.key, self.field, data)
        self.assertEqual(self.db.hget(self.key, self.field), data)

    def test_hmset_hgetall(self):
        data = {'1': 'sdfwevvbg', '2': '345345'}
        self.db.hmset(self.key, data)
        self.assertDictEqual(data, self.db.hgetall(self.key))

    def test_hdel(self):
        data = {'1': 'sdfwevvbg', '2': '345345'}
        self.db.hmset(self.key, data)
        del data['1']
        self.db.hdel(self.key, '1')
        self.assertDictEqual(data, self.db.hgetall(self.key))

    def test_keys(self):
        data = {'1': 'sdfwevvbg', '2': '345345'}
        self.db.hmset(self.key, data)
        self.assertListEqual([self.key], self.db.keys('%s*' % self.key[:3]))

    def test_value(self):
        data = {'1': 'sdfwevvbg', '2': '345345'}
        self.db.hmset(self.key, data)
        self.assertDictEqual(data, self.db.values([self.key])[self.key])

    def test_rename(self):
        data = {'1': 'sdfwevvbg', '2': '345345'}
        self.db.hmset(self.key + self.key, data)
        self.assertDictEqual({}, self.db.values([self.key]))
        self.db.rename(self.key + self.key, self.key)
        self.assertDictEqual(data, self.db.values([self.key])[self.key])





