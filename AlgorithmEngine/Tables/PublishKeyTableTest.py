# coding=utf-8
import unittest
from PublishKeyTable import create
from Common.Dao.ConfigDao import Config


class PublishKeyTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.old = Config.REDIS_HOST
        Config.REDIS_HOST = '10.4.37.206'

    @classmethod
    def tearDownClass(cls):
        Config.REDIS_HOST = cls.old

    def setUp(self):
        self.pt = create()
        self.pk = 'UNITTEST'
        self.pt.insert(self.pk, '单元测试')

    def tearDown(self):
        self.pt.delete(self.pk)

    def test_insert(self):
        self.assertListEqual(self.pt.get_all_data(), [('UNITTEST', '\xe5\x8d\x95\xe5\x85\x83\xe6\xb5\x8b\xe8\xaf\x95', '0', '0')])
        self.assertTupleEqual(self.pt.get_data(self.pk), ('UNITTEST', '\xe5\x8d\x95\xe5\x85\x83\xe6\xb5\x8b\xe8\xaf\x95', '0', '0'))

    def test_delete(self):
        self.pt.delete(self.pk)
        self.assertListEqual(self.pt.get_all_data(), [])

    def test_select_all(self):
        self.assertListEqual(self.pt.select_all(), [self.pk])
        self.pt.insert('UT2')
        self.assertListEqual(self.pt.select_all(), ['UT2', self.pk])
        self.pt.delete('UT2')

    def test_get_state(self):
        self.pt.insert('UT2', state='2')
        self.assertEqual(self.pt.get_state(self.pk), '0')
        self.assertEqual(self.pt.get_state('UT2'), '2')
        self.pt.delete('UT2')

    def test_get_type(self):
        self.pt.insert('UT2', state='2', type='5')
        self.assertEqual(self.pt.get_type(self.pk), '0')
        self.assertEqual(self.pt.get_type('UT2'), '5')
        self.pt.delete('UT2')
