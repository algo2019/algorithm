import unittest

import time

from Common.CacheFunc import cache

__all__ = ['CachePropertyTest']

timeout = 0.2


class ForTest1(object):
    @cache(timeout)
    def func_for_test(self):
        return '1', time.time()


class ForTest2(object):
    @cache(timeout)
    def func_for_test(self):
        return '2:', time.time()


class CachePropertyTest(unittest.TestCase):

    def setUp(self):
        self.t1 = ForTest1()
        self.t2 = ForTest2()

    def test_cache(self):
        frist = self.t1.func_for_test()
        frist2 = self.t2.func_for_test()
        i = 0
        while time.time() - frist[1] < timeout - 0.1:
            i += 1
            self.assertEqual(frist, self.t1.func_for_test())
            self.assertEqual(frist2, self.t2.func_for_test())
            self.assertNotEqual(frist[0], frist2[0])

    def test_refresh(self):
        frist = self.t1.func_for_test()
        frist2 = self.t2.func_for_test()
        time.sleep(timeout)
        self.assertNotEqual(frist, self.t1.func_for_test())
        self.assertNotEqual(frist2, self.t2.func_for_test())
