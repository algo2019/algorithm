import unittest
from Common.AtTimeObjectEngine import ThreadEngine

__all__ = ['ThreadEngineTest']


class ThreadEngineTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_check_self(self):
        e1 = ThreadEngine('1')
        e2 = ThreadEngine('2')
        e1.start()
        e2.start()
        self.assertEqual(0, e1.command_num())
        self.assertEqual(0, e1.command_num())
        e1.stop()
        e2.stop()
